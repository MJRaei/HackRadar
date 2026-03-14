"""
IngestionService — orchestrates RAG ingestion for a project.

Delegates actual ingestion logic to `hackradar.rag.ingestion.ingest_project`.
Also handles Qdrant collection cleanup when a project is deleted.
"""

import asyncio
import logging
from pathlib import Path

from qdrant_client import QdrantClient

from hackradar.config import get_settings
from hackradar.rag.ingestion import ingest_project

logger = logging.getLogger(__name__)
settings = get_settings()


class IngestionService:
    def __init__(self, qdrant_client: QdrantClient) -> None:
        self._qdrant = qdrant_client

    async def ingest(self, project_id: str, local_path: Path) -> int:
        """
        Ingest a project's repository into Qdrant.

        Runs the blocking LlamaIndex/embedding pipeline in a thread pool
        to avoid blocking the async event loop.

        Returns:
            Number of nodes indexed.
        """
        logger.info("Ingesting project %s from %s", project_id, local_path)
        loop = asyncio.get_event_loop()
        node_count = await loop.run_in_executor(
            None,
            lambda: ingest_project(
                project_id=project_id,
                local_path=local_path,
                qdrant_client=self._qdrant,
                embedding_model=settings.embedding_model,
                recreate=True,
            ),
        )
        logger.info("Ingestion done for project %s: %d nodes indexed", project_id, node_count)
        return node_count

    async def delete_collection(self, project_id: str) -> None:
        """Remove the Qdrant collection for a project."""
        collection = f"project_{project_id}"
        if self._qdrant.collection_exists(collection):
            self._qdrant.delete_collection(collection)
            logger.info("Deleted Qdrant collection %s", collection)
