"""
ScoringAgent — scores a single hackathon project against a set of criteria.

The agent receives:
  - project metadata (name, summary, readme excerpt)
  - a list of judging criteria (name, description, weight)
  - a `search_project_code` tool backed by the project's Qdrant collection

It queries the codebase for evidence relevant to each criterion, then
returns a structured JSON score.

Output format:
    {
        "criterion_scores": {
            "Innovation": {"score": 8.0, "rationale": "..."},
            "Technical Complexity": {"score": 7.5, "rationale": "..."}
        },
        "overall_score": 7.8
    }
"""

import logging
from typing import Any

import railtracks as rt

from hackradar.agents.base import BaseAgent
from hackradar.agents.scoring.prompts import SCORING_SYSTEM_PROMPT
from hackradar.agents.scoring.tools import (
    format_criteria,
    format_project_info,
    parse_scoring_output,
)
from hackradar.rag.tools import make_retrieval_tool

logger = logging.getLogger(__name__)


class ScoringAgent(BaseAgent):
    """
    Scores one project against a criteria set using RAG-augmented evaluation.

    The agent is stateless — a new Railtracks agent_node is created per `run()` call
    so each invocation gets a fresh retrieval tool bound to the project's collection.
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
        project_id = project.get("id", "unknown")
        retrieval_tool = make_retrieval_tool(retriever, project_id)

        agent = rt.agent_node(
            name="scoring_agent",
            tool_nodes=[retrieval_tool],
            llm=self.model,
            system_message=SCORING_SYSTEM_PROMPT,
        )

        user_message = (
            f"## Project to Evaluate\n\n{format_project_info(project)}\n\n"
            f"## Judging Criteria\n\n{format_criteria(criteria)}\n\n"
            "Please evaluate this project against all criteria and return the JSON result."
        )

        result = await rt.call(agent, user_message)
        logger.debug("Raw scoring output for %s:\n%s", project_id, result.text)
        return parse_scoring_output(result.text, criteria, project_id)
