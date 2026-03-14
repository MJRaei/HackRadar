from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hackradar.models.category import Category, ProjectCategory
from hackradar.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    model = Category

    async def get_by_name(self, name: str) -> Category | None:
        result = await self._session.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, name: str, description: str | None = None) -> Category:
        existing = await self.get_by_name(name)
        if existing:
            return existing
        category = Category(name=name, description=description)
        return await self.save(category)

    async def get_project_category(
        self, project_id: str, category_id: str
    ) -> ProjectCategory | None:
        result = await self._session.execute(
            select(ProjectCategory).where(
                ProjectCategory.project_id == project_id,
                ProjectCategory.category_id == category_id,
            )
        )
        return result.scalar_one_or_none()

    async def assign_project_to_category(
        self, project_id: str, category_id: str
    ) -> ProjectCategory:
        existing = await self.get_project_category(project_id, category_id)
        if existing:
            return existing
        pc = ProjectCategory(project_id=project_id, category_id=category_id)
        self._session.add(pc)
        await self._session.flush()
        return pc

    async def get_categories_for_project(self, project_id: str) -> list[Category]:
        result = await self._session.execute(
            select(Category)
            .join(ProjectCategory, ProjectCategory.category_id == Category.id)
            .where(ProjectCategory.project_id == project_id)
        )
        return list(result.scalars().all())
