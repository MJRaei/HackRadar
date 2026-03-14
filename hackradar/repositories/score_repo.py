from sqlalchemy import select
from sqlalchemy.orm import joinedload

from hackradar.models.score import Score
from hackradar.repositories.base import BaseRepository


class ScoreRepository(BaseRepository[Score]):
    model = Score

    async def get_by_project(self, project_id: str) -> list[Score]:
        result = await self._session.execute(
            select(Score)
            .where(Score.project_id == project_id)
            .options(joinedload(Score.criteria_set))
        )
        return list(result.scalars().all())

    async def get_by_project_and_criteria(
        self, project_id: str, criteria_set_id: str
    ) -> Score | None:
        result = await self._session.execute(
            select(Score).where(
                Score.project_id == project_id,
                Score.criteria_set_id == criteria_set_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_rankings(self, criteria_set_id: str) -> list[Score]:
        """Return scores for a criteria set ordered by overall_score descending."""
        result = await self._session.execute(
            select(Score)
            .where(Score.criteria_set_id == criteria_set_id)
            .order_by(Score.overall_score.desc().nulls_last())
            .options(joinedload(Score.project))
        )
        return list(result.scalars().all())
