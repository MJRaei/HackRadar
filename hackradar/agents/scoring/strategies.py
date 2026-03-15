"""
Two scoring strategies for different LLM backends.

- ToolCallStrategy:     model uses `search_project_code` and `google_search` tool calls
                        (Gemini, OpenAI). The agent decides when to invoke each tool.
- RAGPrefetchStrategy:  code evidence is pre-fetched and injected into the prompt.
                        Web search results are always pre-fetched and injected; the LLM
                        decides which criteria benefit from them.
                        Used for endpoints that don't support function calling (e.g. GPT-OSS).
"""

import logging
from typing import Any

import railtracks as rt

from hackradar.agents.scoring.prompts import (
    SCORING_SYSTEM_PROMPT,
    SCORING_SYSTEM_PROMPT_NO_TOOLS,
)
from hackradar.agents.scoring.tools import (
    format_criteria,
    format_project_info,
    parse_scoring_output,
)
from hackradar.agents.strategies.base import Strategy
from hackradar.agents.tools.web_search import google_search, prefetch_similar_projects
from hackradar.rag.tools import make_retrieval_tool

logger = logging.getLogger(__name__)


class ToolCallStrategy(Strategy):
    """Scoring via LLM tool calls. Requires function-calling support."""

    async def run(
        self,
        model: Any,
        project: dict[str, Any],
        criteria: list[dict[str, Any]],
        retriever: Any,
    ) -> dict[str, Any]:
        project_id = project.get("id", "unknown")
        retrieval_tool = make_retrieval_tool(retriever, project_id)

        agent = rt.agent_node(
            name="scoring_agent",
            tool_nodes=[retrieval_tool, google_search],
            llm=model,
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


class RAGPrefetchStrategy(Strategy):
    """Scoring via pre-fetched code context. Works with any LLM backend."""

    async def run(
        self,
        model: Any,
        project: dict[str, Any],
        criteria: list[dict[str, Any]],
        retriever: Any,
    ) -> dict[str, Any]:
        project_id = project.get("id", "unknown")
        code_context = self._prefetch(criteria, retriever, project_id)

        query = (
            f"{project.get('name', '')} {project.get('summary') or ''} "
            "similar projects open source"
        ).strip()
        web_section = await prefetch_similar_projects(query)

        agent = rt.agent_node(
            name="scoring_agent",
            tool_nodes=[],
            llm=model,
            system_message=SCORING_SYSTEM_PROMPT_NO_TOOLS,
        )

        user_message = (
            f"## Project to Evaluate\n\n{format_project_info(project)}\n\n"
            f"## Judging Criteria\n\n{format_criteria(criteria)}\n\n"
            f"## Retrieved Code Evidence\n\n{code_context}\n\n"
        )

        if web_section:
            user_message += f"## Similar Projects Found Online\n\n{web_section}\n\n"

        user_message += "Please evaluate this project against all criteria and return the JSON result."

        result = await rt.call(agent, user_message)
        logger.debug("Raw scoring output for %s:\n%s", project_id, result.text)
        return parse_scoring_output(result.text, criteria, project_id)

    def _prefetch(
        self,
        criteria: list[dict[str, Any]],
        retriever: Any,
        project_id: str,
    ) -> str:
        """Retrieve code snippets for each criterion and format them as context."""
        sections: list[str] = []

        for criterion in criteria:
            queries = [criterion["name"], criterion.get("description", "")[:120]]
            seen: set[str] = set()
            chunks: list[str] = []

            for query in queries:
                try:
                    nodes = retriever.retrieve(query)
                except Exception as exc:
                    logger.error(
                        "Retrieval failed for project %s, criterion %s: %s",
                        project_id,
                        criterion["name"],
                        exc,
                    )
                    continue

                for node in nodes:
                    content = node.get_content()
                    if content not in seen:
                        seen.add(content)
                        file_path = node.metadata.get("file_path", "unknown")
                        chunks.append(f"({file_path})\n{content}")

            body = "\n\n".join(chunks) if chunks else "[No relevant code found]"
            sections.append(f"### {criterion['name']}\n{body}")

        return "\n\n".join(sections)
