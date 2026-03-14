"""
ScoringService — orchestrates project scoring via ScoringAgent.

For each project:
1. Retrieve the project record and criteria set from DB
2. Build a LlamaIndex retriever for the project's Qdrant collection
3. Run ScoringAgent (ADK) — the agent queries code via RAG and scores each criterion
4. Persist the Score record
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client import QdrantClient

from hackradar.agents.scoring import ScoringAgent
from hackradar.config import get_settings
from hackradar.models.score import Score
from hackradar.repositories.criteria_repo import CriteriaRepository
from hackradar.repositories.project_repo import ProjectRepository
from hackradar.repositories.score_repo import ScoreRepository
from hackradar.rag.retriever import get_retriever

logger = logging.getLogger(__name__)
settings = get_settings()


class ScoringService:
    def __init__(self, session: AsyncSession, qdrant_client: QdrantClient) -> None:
        self._project_repo = ProjectRepository(session)
        self._criteria_repo = CriteriaRepository(session)
        self._score_repo = ScoreRepository(session)
        self._qdrant = qdrant_client

    async def score_projects(
        self, project_ids: list[str], criteria_set_id: str
    ) -> list[Score]:
        """
        Score multiple projects against a criteria set.

        Args:
            project_ids:     IDs of projects to score.
            criteria_set_id: ID of the CriteriaSet to evaluate against.

        Returns:
            List of saved Score records.
        """
        criteria_set = await self._criteria_repo.get(criteria_set_id)
        if not criteria_set:
            raise ValueError(f"CriteriaSet {criteria_set_id} not found")

        criteria = criteria_set.criteria  # list of dicts from JSON column

        projects = await self._project_repo.get_by_ids(project_ids)
        if not projects:
            raise ValueError("No projects found for the provided IDs")

        agent = ScoringAgent(model=settings.llm_model)
        results: list[Score] = []

        for project in projects:
            logger.info("Scoring project %s (%s)", project.id, project.name)

            if project.local_path is None:
                logger.warning("Project %s has no local_path — skipping", project.id)
                continue

            try:
                retriever = get_retriever(
                    project_id=project.id,
                    qdrant_client=self._qdrant,
                    embedding_model=settings.embedding_model,
                )
            except ValueError as exc:
                logger.error("Cannot create retriever for project %s: %s", project.id, exc)
                continue

            project_dict = {
                "id": project.id,
                "name": project.name,
                "summary": project.summary,
                "readme": project.readme,
            }

            result = await agent.run(
                project=project_dict,
                criteria=criteria,
                retriever=retriever,
            )

            # Upsert: replace existing score for this project+criteria combination
            existing = await self._score_repo.get_by_project_and_criteria(
                project.id, criteria_set_id
            )
            if existing:
                existing.criterion_scores = result.get("criterion_scores", {})
                existing.overall_score = result.get("overall_score")
                score = await self._score_repo.save(existing)
            else:
                score = Score(
                    project_id=project.id,
                    criteria_set_id=criteria_set_id,
                    criterion_scores=result.get("criterion_scores", {}),
                    overall_score=result.get("overall_score"),
                )
                score = await self._score_repo.save(score)

            results.append(score)
            logger.info(
                "Scored project %s: overall=%.2f",
                project.id,
                score.overall_score or 0.0,
            )

        return results

    async def get_rankings(
        self, criteria_set_id: str
    ) -> list[dict[str, Any]]:
        """Return projects ranked by overall score for a criteria set."""
        scores = await self._score_repo.get_rankings(criteria_set_id)
        rankings = []
        for rank, score in enumerate(scores, 1):
            rankings.append({
                "rank": rank,
                "project_id": score.project_id,
                "project_name": score.project.name if score.project else "Unknown",
                "overall_score": score.overall_score,
                "criteria_set_id": score.criteria_set_id,
            })
        return rankings
