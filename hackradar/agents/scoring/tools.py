import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def format_criteria(criteria: list[dict]) -> str:
    lines = []
    for c in criteria:
        lines.append(f"- **{c['name']}** (weight: {c.get('weight', 1.0)}): {c['description']}")
    return "\n".join(lines)


def format_project_info(project: dict) -> str:
    name = project.get("name", "Unknown")
    summary = project.get("summary") or "No summary provided."
    readme = project.get("readme") or "No README available."
    readme_excerpt = readme[:2000] + "..." if len(readme) > 2000 else readme
    return (
        f"**Project Name:** {name}\n\n"
        f"**Summary:** {summary}\n\n"
        f"**README (excerpt):**\n{readme_excerpt}"
    )


def parse_scoring_output(
    raw: str, criteria: list[dict], project_id: str
) -> dict[str, Any]:
    """Extract JSON from agent output, with a safe fallback."""
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()

    try:
        data = json.loads(text)
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
