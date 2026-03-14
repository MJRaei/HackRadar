import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def format_projects_input(projects: list[dict]) -> str:
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


def parse_categorization_output(raw: str, projects: list[dict]) -> dict[str, Any]:
    """Extract JSON from agent output with a safe fallback."""
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error("Failed to parse categorization output:\n%s", raw)
        return {
            "assignments": {p["id"]: "Uncategorized" for p in projects},
            "categories": ["Uncategorized"],
            "_parse_error": "Agent returned invalid JSON",
        }
