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

import json
import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from hackradar.agents.base import BaseAgent
from hackradar.rag.tools import make_retrieval_tool

logger = logging.getLogger(__name__)

SCORING_SYSTEM_PROMPT = """You are an expert hackathon judge evaluating a software project.

You will be given:
1. Project information (name, summary, README)
2. A list of judging criteria, each with a name, description, and weight
3. Access to a tool `search_project_code` that searches the project's source code

## Your Task
For EACH criterion:
1. Use `search_project_code` to retrieve relevant code evidence (2-3 targeted queries per criterion)
2. Assess the code quality and implementation against the criterion description
3. Assign a score from 0.0 to 10.0 (floats allowed, e.g. 7.5)
4. Write a concise rationale (2-4 sentences) citing specific evidence from the code

## Output
After evaluating all criteria, output ONLY a valid JSON object in this exact format:
```json
{
  "criterion_scores": {
    "<criterion_name>": {"score": <float 0-10>, "rationale": "<string>"},
    ...
  },
  "overall_score": <weighted_average_float>
}
```

The overall_score is the weighted average of all criterion scores using the provided weights.
Do not include any text outside the JSON block.
"""


def _format_criteria(criteria: list[dict]) -> str:
    lines = []
    for c in criteria:
        lines.append(f"- **{c['name']}** (weight: {c.get('weight', 1.0)}): {c['description']}")
    return "\n".join(lines)


def _format_project_info(project: dict) -> str:
    name = project.get("name", "Unknown")
    summary = project.get("summary") or "No summary provided."
    readme = project.get("readme") or "No README available."
    readme_excerpt = readme[:2000] + "..." if len(readme) > 2000 else readme
    return (
        f"**Project Name:** {name}\n\n"
        f"**Summary:** {summary}\n\n"
        f"**README (excerpt):**\n{readme_excerpt}"
    )


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
            f"## Project to Evaluate\n\n{_format_project_info(project)}\n\n"
            f"## Judging Criteria\n\n{_format_criteria(criteria)}\n\n"
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

        return _parse_scoring_output(result_text, criteria, project_id)


def _parse_scoring_output(
    raw: str, criteria: list[dict], project_id: str
) -> dict[str, Any]:
    """Extract JSON from agent output, with a safe fallback."""
    # Strip markdown code fences if present
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()

    try:
        data = json.loads(text)
        # Ensure overall_score is present
        if "overall_score" not in data and "criterion_scores" in data:
            scores_dict = data["criterion_scores"]
            total_weight = sum(c.get("weight", 1.0) for c in criteria)
            weighted_sum = sum(
                scores_dict.get(c["name"], {}).get("score", 0) * c.get("weight", 1.0)
                for c in criteria
            )
            data["overall_score"] = round(weighted_sum / total_weight, 2) if total_weight else None
        return data
    except json.JSONDecodeError:
        logger.error("Failed to parse scoring output for project %s:\n%s", project_id, raw)
        return {
            "criterion_scores": {},
            "overall_score": None,
            "_parse_error": "Agent returned invalid JSON",
            "_raw": raw,
        }
