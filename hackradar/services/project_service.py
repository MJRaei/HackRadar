"""
ProjectService — manages project lifecycle.

Responsibilities:
- Create a project record in the DB
- Clone the GitHub repository locally
- Extract README content
- Trigger RAG ingestion via IngestionService
- Update project status throughout
"""

import logging
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hackradar.services.ingestion_service import IngestionService

import httpx
from git import Repo, GitCommandError
from sqlalchemy.ext.asyncio import AsyncSession

from hackradar.config import get_settings
from hackradar.db.session import AsyncSessionLocal
from hackradar.models.project import Project, ProjectStatus
from hackradar.repositories.project_repo import ProjectRepository
from hackradar.schemas.project import ProjectCreate

logger = logging.getLogger(__name__)
settings = get_settings()


def _repo_local_path(project_id: str) -> Path:
    base = Path(settings.repos_base_dir)
    base.mkdir(parents=True, exist_ok=True)
    return base / project_id


def _extract_readme(local_path: Path) -> str | None:
    """Try common README filenames and return the content of the first found."""
    candidates = ["README.md", "README.rst", "README.txt", "readme.md", "Readme.md"]
    for name in candidates:
        readme_path = local_path / name
        if readme_path.exists():
            try:
                return readme_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
    return None


def _clone_repo(github_url: str, local_path: Path) -> None:
    if local_path.exists():
        shutil.rmtree(local_path)
    Repo.clone_from(github_url, str(local_path), depth=1)


def _strip_git_dir(local_path: Path) -> None:
    """Remove .git so the clone isn't detected as a nested git repo."""
    git_dir = local_path / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir)


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ProjectRepository(session)

    async def create(self, data: ProjectCreate) -> Project:
        """
        Create a new project record.

        Cloning and ingestion are triggered separately via `ingest()`
        to allow the API to return immediately and process in background.
        """
        existing = await self._repo.get_by_github_url(data.github_url)
        if existing:
            raise ValueError(f"Project with URL '{data.github_url}' already exists (id={existing.id})")

        project = Project(
            name=data.name,
            github_url=data.github_url,
            summary=data.summary,
            status=ProjectStatus.PENDING,
        )
        saved = await self._repo.save(project)
        await self._repo._session.commit()
        return saved

    async def clone_and_index(self, project_id: str, ingestion_service: "IngestionService") -> Project:
        """
        Clone the repository, extract README, and trigger RAG ingestion.

        This is designed to be called as a background task after project creation.
        Uses its own session so it doesn't block the POST request's session from
        committing (which would make the project invisible to other requests until
        ingestion completes).
        """
        async with AsyncSessionLocal() as session:
            repo = ProjectRepository(session)

            project = await repo.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")

            local_path = _repo_local_path(project_id)

            # Clone
            project.status = ProjectStatus.CLONING
            await repo.save(project)
            await session.commit()
            try:
                logger.info("Cloning %s → %s", project.github_url, local_path)
                _clone_repo(project.github_url, local_path)
                _strip_git_dir(local_path)
            except GitCommandError as exc:
                project.status = ProjectStatus.FAILED
                project.error_message = f"Clone failed: {exc}"
                await repo.save(project)
                await session.commit()
                raise

            project.local_path = str(local_path)
            project.readme = _extract_readme(local_path)

            # Ingest
            project.status = ProjectStatus.INDEXING
            await repo.save(project)
            await session.commit()
            try:
                await ingestion_service.ingest(project_id, local_path)
            except Exception as exc:
                project.status = ProjectStatus.FAILED
                project.error_message = f"Ingestion failed: {exc}"
                await repo.save(project)
                await session.commit()
                raise

            project.status = ProjectStatus.INDEXED
            project.error_message = None
            result = await repo.save(project)
            await session.commit()
            return result

    async def get(self, project_id: str) -> Project | None:
        return await self._repo.get(project_id)

    async def list_all(self, offset: int = 0, limit: int = 100) -> tuple[list[Project], int]:
        items = await self._repo.get_all(offset=offset, limit=limit)
        total = await self._repo.count()
        return items, total

    async def delete(self, project_id: str) -> None:
        project = await self._repo.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Remove cloned repo from disk
        if project.local_path:
            local_path = Path(project.local_path)
            if local_path.exists():
                shutil.rmtree(local_path, ignore_errors=True)

        await self._repo.delete(project)
