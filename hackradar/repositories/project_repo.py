from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hackradar.models.project import Project
from hackradar.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    model = Project

    async def get_by_github_url(self, github_url: str) -> Project | None:
        result = await self._session.execute(
            select(Project).where(Project.github_url == github_url)
        )
        return result.scalar_one_or_none()

    async def get_by_status(self, status: str) -> list[Project]:
        result = await self._session.execute(
            select(Project).where(Project.status == status)
        )
        return list(result.scalars().all())

    async def get_by_ids(self, ids: list[str]) -> list[Project]:
        result = await self._session.execute(
            select(Project).where(Project.id.in_(ids))
        )
        return list(result.scalars().all())
