"""
ScoringAgent — scores a single hackathon project against a set of criteria.

Automatically selects a scoring strategy based on the LLM backend:
  - ToolCallStrategy:    for models that support function calling (Gemini, OpenAI).
  - RAGPrefetchStrategy: for endpoints that don't (e.g. self-hosted GPT-OSS).
"""

import logging
from typing import Any

from hackradar.agents.base import BaseAgent
from hackradar.agents.llm import OpenAICompatibleLLM
from hackradar.agents.scoring.strategies import RAGPrefetchStrategy, ToolCallStrategy

logger = logging.getLogger(__name__)


class ScoringAgent(BaseAgent):
    """
    Scores one project against a criteria set using RAG-augmented evaluation.

    A new strategy instance is created per `run()` call so each invocation
    gets a fresh context bound to the project's collection.
    """

    async def run(
        self,
        project: dict[str, Any],
        criteria: list[dict[str, Any]],
        retriever: Any,
    ) -> dict[str, Any]:
        """
        Args:
            project:   Dict with keys: id, name, summary, readme.
            criteria:  List of dicts: [{name, description, weight}, ...].
            retriever: LlamaIndex BaseRetriever for the project's Qdrant collection.

        Returns:
            Dict: {criterion_scores: {...}, overall_score: float}
        """
        strategy = (
            RAGPrefetchStrategy()
            if isinstance(self.model, OpenAICompatibleLLM)
            else ToolCallStrategy()
        )
        logger.debug(
            "Scoring project %s using %s",
            project.get("id"),
            type(strategy).__name__,
        )
        return await strategy.run(self.model, project, criteria, retriever)
