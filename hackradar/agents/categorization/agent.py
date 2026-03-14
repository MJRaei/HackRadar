"""
CategorizationAgent — categorizes all hackathon projects at once.

The agent receives summaries and README excerpts for ALL projects and
either assigns them to user-provided categories or auto-discovers clusters.

Processing all projects in a single call ensures globally coherent
categorization (e.g., no duplicate cluster labels, balanced distribution).

Output format:
    {
        "assignments": {
            "<project_id>": "<category_name>",
            ...
        },
        "categories": ["Web App", "AI/ML", "DevTools", ...]
    }
"""

import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from hackradar.agents.base import BaseAgent
from hackradar.agents.categorization.prompts import (
    AUTO_CATEGORIZATION_INSTRUCTIONS,
    CATEGORIZATION_SYSTEM_PROMPT,
    PREDEFINED_CATEGORIES_INSTRUCTIONS,
)
from hackradar.agents.categorization.tools import (
    format_projects_input,
    parse_categorization_output,
)

logger = logging.getLogger(__name__)


class CategorizationAgent(BaseAgent):
    """
    Categorizes all projects in a single LLM call for global coherence.

    Supports two modes:
    - Predefined: user supplies a list of category names
    - Auto-discover: agent determines the best categories
    """

    async def run(
        self,
        projects: list[dict[str, Any]],
        categories: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Args:
            projects:   List of project dicts: [{id, name, summary, readme}, ...].
            categories: Optional list of category names. If None, auto-discover.

        Returns:
            Dict: {assignments: {project_id: category}, categories: [str]}
        """
        if categories:
            mode_instructions = PREDEFINED_CATEGORIES_INSTRUCTIONS.format(
                categories="\n".join(f"- {c}" for c in categories)
            )
        else:
            mode_instructions = AUTO_CATEGORIZATION_INSTRUCTIONS

        system_prompt = CATEGORIZATION_SYSTEM_PROMPT.format(
            mode_instructions=mode_instructions
        )

        agent = LlmAgent(
            name="categorization_agent",
            model=self.model,
            instruction=system_prompt,
            tools=[],
        )

        session_service = InMemorySessionService()
        runner = Runner(
            agent=agent, app_name="hackradar_categorizer", session_service=session_service
        )

        session = await session_service.create_session(
            app_name="hackradar_categorizer", user_id="system"
        )

        projects_text = format_projects_input(projects)
        user_message = (
            f"Please categorize the following {len(projects)} hackathon projects.\n\n"
            f"{projects_text}\n\n"
            "Return the JSON categorization result."
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

        return parse_categorization_output(result_text, projects)
