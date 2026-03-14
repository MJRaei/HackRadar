from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hackradar.models.criteria import CriteriaSet
from hackradar.repositories.base import BaseRepository


class CriteriaRepository(BaseRepository[CriteriaSet]):
    model = CriteriaSet

    async def get_by_name(self, name: str) -> CriteriaSet | None:
        result = await self._session.execute(
            select(CriteriaSet).where(CriteriaSet.name == name)
        )
        return result.scalar_one_or_none()
