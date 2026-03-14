"""
Railtracks-compatible tool wrappers for LlamaIndex retrievers.

`make_retrieval_tool` wraps a LlamaIndex `BaseRetriever` as a Railtracks
function_node so scoring agents can call it to fetch relevant code snippets.
"""

import logging
from typing import Any

import railtracks as rt
from llama_index.core.retrievers import BaseRetriever

logger = logging.getLogger(__name__)


def make_retrieval_tool(retriever: BaseRetriever, project_id: str) -> Any:
    """
    Wrap a LlamaIndex retriever as a Railtracks function_node.

    The returned tool has the signature:
        search_project_code(query: str) -> str

    The agent calls this tool with a natural-language query and receives
    the top-k relevant code chunks concatenated as a single string.

    Args:
        retriever:   LlamaIndex retriever already configured for a project.
        project_id:  Used in log messages for clarity.

    Returns:
        A Railtracks function_node the agent can invoke.
    """

    @rt.function_node
    def search_project_code(query: str) -> str:
        """
        Search the project's source code for passages relevant to the query.

        Use this tool to retrieve code snippets, function implementations,
        or architectural patterns before scoring a criterion.

        Args:
            query (str): A natural-language description of what to look for in the code.

        Returns:
            Concatenated relevant code snippets with file path metadata.
        """
        logger.debug("RAG query for project %s: %r", project_id, query)
        try:
            nodes = retriever.retrieve(query)
        except Exception as exc:
            logger.error("Retrieval failed for project %s: %s", project_id, exc)
            return f"[Retrieval error: {exc}]"

        if not nodes:
            return "[No relevant code found for this query]"

        parts: list[str] = []
        for i, node in enumerate(nodes, 1):
            file_path = node.metadata.get("file_path", "unknown")
            parts.append(f"--- Chunk {i} ({file_path}) ---\n{node.get_content()}")

        return "\n\n".join(parts)

    return search_project_code
