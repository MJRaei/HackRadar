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

import json
import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from hackradar.agents.base import BaseAgent

logger = logging.getLogger(__name__)

CATEGORIZATION_SYSTEM_PROMPT = """You are an expert hackathon organizer tasked with categorizing projects.

You will receive summaries and README excerpts for multiple hackathon projects.

## Your Task

{mode_instructions}

## Output
Output ONLY a valid JSON object in this exact format:
```json
{{
  "assignments": {{
    "<project_id>": "<category_name>",
    ...
  }},
  "categories": ["<category_name_1>", "<category_name_2>", ...]
}}
```

Rules:
- Every project_id in the input must appear in `assignments`
- `categories` lists all distinct categories used
- Category names should be concise (2-4 words), clear, and consistent
- Do not include any text outside the JSON block
"""

PREDEFINED_CATEGORIES_INSTRUCTIONS = """The user has defined the following categories:
{categories}

Assign each project to the SINGLE most appropriate category from this list.
If a project fits multiple categories, choose the primary one.
"""

AUTO_CATEGORIZATION_INSTRUCTIONS = """Auto-discover meaningful clusters from the projects.
- Aim for 3-8 categories depending on the diversity of projects
- Use descriptive, consistent category names (e.g., "AI/ML Tools", "Web Apps", "DevTools", "Blockchain/Web3")
- Group thematically similar projects together
- Avoid overly specific or overly broad categories
"""


def _format_projects_input(projects: list[dict]) -> str:
    parts = []
    for p in projects:
        project_id = p.get("id", "unknown")
        name = p.get("name", "Unknown")
        summary = p.get("summary") or "No summary."
        readme = p.get("readme") or ""
        readme_excerpt = readme[:500] + "..." if len(readme) > 500 else readme

        parts.append(
            f"### Project ID: {project_id}\n"
            f"**Name:** {name}\n"
            f"**Summary:** {summary}\n"
            f"**README (excerpt):** {readme_excerpt}\n"
        )
    return "\n---\n".join(parts)


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
            tools=[],  # No tools needed — works on provided text only
        )

        session_service = InMemorySessionService()
        runner = Runner(
            agent=agent, app_name="hackradar_categorizer", session_service=session_service
        )

        session = await session_service.create_session(
            app_name="hackradar_categorizer", user_id="system"
        )

        projects_text = _format_projects_input(projects)
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

        return _parse_categorization_output(result_text, projects)


def _parse_categorization_output(raw: str, projects: list[dict]) -> dict[str, Any]:
    """Extract JSON from agent output with a safe fallback."""
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()

    try:
        data = json.loads(text)
        return data
    except json.JSONDecodeError:
        logger.error("Failed to parse categorization output:\n%s", raw)
        # Fallback: assign all to "Uncategorized"
        return {
            "assignments": {p["id"]: "Uncategorized" for p in projects},
            "categories": ["Uncategorized"],
            "_parse_error": "Agent returned invalid JSON",
        }
