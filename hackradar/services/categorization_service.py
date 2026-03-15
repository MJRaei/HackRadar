"""
CategorizationService — orchestrates project categorization via CategorizationAgent.

Fetches all requested projects' summaries and READMEs, runs the ADK
CategorizationAgent on all of them in one call, then persists the
Category and ProjectCategory records.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from hackradar.agents.categorization import CategorizationAgent
from hackradar.agents.llm import create_model_from_settings
from hackradar.config import get_settings
from hackradar.repositories.category_repo import CategoryRepository
from hackradar.repositories.project_repo import ProjectRepository
from hackradar.schemas.category import CategorizationResponse, ProjectCategoryAssignment

logger = logging.getLogger(__name__)
settings = get_settings()


class CategorizationService:
    def __init__(self, session: AsyncSession) -> None:
        self._project_repo = ProjectRepository(session)
        self._category_repo = CategoryRepository(session)

    async def categorize(
        self,
        project_ids: list[str],
        categories: list[str] | None = None,
    ) -> CategorizationResponse:
        """
        Categorize a list of projects.

        Args:
            project_ids: IDs of projects to categorize.
            categories:  Optional user-defined category list. If None, auto-discover.

        Returns:
            CategorizationResponse with per-project assignments.
        """
        projects = await self._project_repo.get_by_ids(project_ids)
        if not projects:
            raise ValueError("No projects found for the provided IDs")

        project_dicts = [
            {
                "id": p.id,
                "name": p.name,
                "summary": p.summary,
                "readme": p.readme,
            }
            for p in projects
        ]

        agent = CategorizationAgent(model=create_model_from_settings(settings))
        result = await agent.run(projects=project_dicts, categories=categories)

        assignments_map: dict[str, str] = result.get("assignments", {})
        categories_created: list[str] = []

        assignments: list[ProjectCategoryAssignment] = []
        project_name_map = {p.id: p.name for p in projects}

        for project_id, category_name in assignments_map.items():
            category = await self._category_repo.get_or_create(category_name)

            if category_name not in categories_created:
                categories_created.append(category_name)

            await self._category_repo.assign_project_to_category(project_id, category.id)

            assignments.append(
                ProjectCategoryAssignment(
                    project_id=project_id,
                    project_name=project_name_map.get(project_id, "Unknown"),
                    category=category_name,
                )
            )
            logger.info("Assigned project %s → %s", project_id, category_name)

        return CategorizationResponse(
            assignments=assignments,
            categories_created=categories_created,
        )
