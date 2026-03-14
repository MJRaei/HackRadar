"""
BulkUploadService — orchestrates file-based bulk project creation.

Responsibilities:
1. Parse the uploaded file with the appropriate FileParser.
2. Extract GitHub URLs via GitHubUrlExtractor.
3. Derive a project name from each repo URL.
4. Attempt to create each project via ProjectService.
5. Return a result object distinguishing queued vs skipped projects.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from hackradar.models.project import Project
from hackradar.schemas.project import ProjectCreate
from hackradar.services.bulk_upload.extractor import GitHubUrlExtractor
from hackradar.services.bulk_upload.parsers import FileParserFactory

if TYPE_CHECKING:
    from fastapi import BackgroundTasks
    from hackradar.services.ingestion_service import IngestionService
    from hackradar.services.project_service import ProjectService

logger = logging.getLogger(__name__)


@dataclass
class SkippedProject:
    url: str
    reason: str


@dataclass
class BulkUploadResult:
    queued: list[Project] = field(default_factory=list)
    skipped: list[SkippedProject] = field(default_factory=list)
    total_found: int = 0


def _derive_name(github_url: str) -> str:
    """Extract the repository name from a GitHub URL."""
    return github_url.rstrip("/").split("/")[-1]


class BulkUploadService:
    def __init__(self, project_service: ProjectService) -> None:
        self._project_service = project_service
        self._extractor = GitHubUrlExtractor()

    async def process(
        self,
        file_content: str,
        file_extension: str,
        background_tasks: BackgroundTasks,
        ingestion_service: IngestionService,
    ) -> BulkUploadResult:
        """
        Parse *file_content*, extract GitHub URLs, and queue each as a project.

        Projects that already exist (duplicate URL) are recorded in
        ``result.skipped`` rather than raising an error.
        """
        parser = FileParserFactory.create(file_extension)
        tokens = parser.parse(file_content)
        urls = self._extractor.extract(tokens)

        result = BulkUploadResult(total_found=len(urls))

        for url in urls:
            name = _derive_name(url)
            try:
                project = await self._project_service.create(
                    ProjectCreate(name=name, github_url=url)
                )
                background_tasks.add_task(
                    self._project_service.clone_and_index,
                    project_id=project.id,
                    ingestion_service=ingestion_service,
                )
                result.queued.append(project)
                logger.info("Queued project '%s' (%s)", name, url)
            except ValueError as exc:
                result.skipped.append(SkippedProject(url=url, reason=str(exc)))
                logger.info("Skipped '%s': %s", url, exc)

        return result
