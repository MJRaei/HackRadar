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

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

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

    The agent is stateless — a new ADK Runner is created per `run()` call.
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

        agent = LlmAgent(
            name="scoring_agent",
            model=self.model,
            instruction=SCORING_SYSTEM_PROMPT,
            tools=[retrieval_tool],
        )

        session_service = InMemorySessionService()
        runner = Runner(agent=agent, app_name="hackradar_scorer", session_service=session_service)

        session = await session_service.create_session(
            app_name="hackradar_scorer", user_id="system"
        )

        user_message = (
            f"## Project to Evaluate\n\n{format_project_info(project)}\n\n"
            f"## Judging Criteria\n\n{format_criteria(criteria)}\n\n"
            "Please evaluate this project against all criteria and return the JSON result."
        )

        result_text = ""
        async for event in runner.run_async(
            user_id="system",
            session_id=session.id,
            new_message=Content(role="user", parts=[Part(text=user_message)]),
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        result_text += part.text

        return parse_scoring_output(result_text, criteria, project_id)
