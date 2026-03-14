"""
Retriever factory for per-project Qdrant collections.

Usage:
    retriever = get_retriever(project_id, qdrant_client)
    nodes = retriever.retrieve("authentication logic")
"""

import logging

from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import BaseRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


def get_retriever(
    project_id: str,
    qdrant_client: QdrantClient,
    embedding_model: str = "allenai-specter",
    top_k: int = 8,
) -> BaseRetriever:
    """
    Build a LlamaIndex retriever backed by the project's Qdrant collection.

    Args:
        project_id:      Project identifier — collection name is `project_{project_id}`.
        qdrant_client:   Connected Qdrant client.
        embedding_model: Must match the model used during ingestion.
        top_k:           Number of nodes to retrieve per query.

    Returns:
        A LlamaIndex BaseRetriever ready to call `.retrieve(query)`.
    """
    collection = f"project_{project_id}"

    if not qdrant_client.collection_exists(collection):
        raise ValueError(
            f"Collection '{collection}' does not exist. "
            "Ensure the project has been ingested before scoring."
        )

    embed_model = HuggingFaceEmbedding(model_name=embedding_model, trust_remote_code=True)
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=collection)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)

    logger.debug("Retriever created for project %s (top_k=%d)", project_id, top_k)
    return index.as_retriever(similarity_top_k=top_k)
