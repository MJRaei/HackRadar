"""
RAG ingestion pipeline.

For each project:
  1. Load code files with LlamaIndex SimpleDirectoryReader
  2. Chunk with CodeSplitter (tree-sitter, respects function/class boundaries)
  3. Embed with allenai-specter via HuggingFaceEmbedding
  4. Index into a per-project Qdrant collection

The collection is named `project_{project_id}` and persists across restarts
via the Qdrant Docker volume.

Re-running ingestion on an existing project recreates the collection to keep
embeddings consistent with the current code state.
"""

import logging
from pathlib import Path

from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import CodeSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

logger = logging.getLogger(__name__)

# File extensions we want to index
SUPPORTED_EXTENSIONS = [
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".go", ".rs", ".java", ".cpp", ".c", ".h",
    ".rb", ".php", ".swift", ".kt", ".cs",
    ".sol",  # Solidity (common in hackathons)
]

# Language mapping for tree-sitter CodeSplitter
EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".cs": "c_sharp",
    ".sol": "solidity",
}

# Embedding dimension for allenai-specter
SPECTER_DIMENSION = 768


def _collection_name(project_id: str) -> str:
    return f"project_{project_id}"


def _get_embed_model(model_name: str) -> HuggingFaceEmbedding:
    return HuggingFaceEmbedding(model_name=model_name, trust_remote_code=True)


def _ensure_collection(client: QdrantClient, collection: str, recreate: bool = False) -> None:
    exists = client.collection_exists(collection)
    if exists and recreate:
        client.delete_collection(collection)
        exists = False
    if not exists:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=SPECTER_DIMENSION, distance=Distance.COSINE),
        )


def ingest_project(
    project_id: str,
    local_path: Path,
    qdrant_client: QdrantClient,
    embedding_model: str = "allenai-specter",
    recreate: bool = True,
) -> int:
    """
    Ingest a cloned repository into Qdrant.

    Args:
        project_id:      Unique project identifier (used as collection name suffix).
        local_path:      Path to the cloned repository on disk.
        qdrant_client:   Connected Qdrant client.
        embedding_model: HuggingFace model name for embeddings.
        recreate:        If True, drop and recreate the collection before ingestion.

    Returns:
        Number of nodes indexed.
    """
    collection = _collection_name(project_id)
    logger.info("Starting ingestion for project %s → collection %s", project_id, collection)

    # Ensure Qdrant collection exists
    _ensure_collection(qdrant_client, collection, recreate=recreate)

    # Load code files
    try:
        docs = SimpleDirectoryReader(
            input_dir=str(local_path),
            required_exts=SUPPORTED_EXTENSIONS,
            recursive=True,
            exclude_hidden=True,
        ).load_data()
    except ValueError:
        logger.warning("No supported code files found in %s", local_path)
        return 0

    if not docs:
        logger.warning("No documents loaded from %s", local_path)
        return 0

    logger.info("Loaded %d documents from %s", len(docs), local_path)

    # Build per-language splitters (CodeSplitter is language-specific)
    # Group docs by extension and split each group with the appropriate splitter
    from collections import defaultdict
    from llama_index.core.schema import Document

    ext_groups: dict[str, list[Document]] = defaultdict(list)
    for doc in docs:
        file_path = doc.metadata.get("file_path", "")
        ext = Path(file_path).suffix.lower()
        ext_groups[ext].append(doc)

    all_nodes = []
    embed_model = _get_embed_model(embedding_model)

    for ext, ext_docs in ext_groups.items():
        language = EXTENSION_TO_LANGUAGE.get(ext, "python")
        try:
            splitter = CodeSplitter(
                language=language,
                chunk_lines=40,
                chunk_lines_overlap=5,
                max_chars=1500,
            )
            nodes = splitter.get_nodes_from_documents(ext_docs)
            all_nodes.extend(nodes)
            logger.debug("Split %d docs (%s) → %d nodes", len(ext_docs), language, len(nodes))
        except Exception as exc:
            # Fall back: include docs as-is if tree-sitter parsing fails for that language
            logger.warning("CodeSplitter failed for %s (%s): %s — using raw docs", ext, language, exc)
            all_nodes.extend(ext_docs)  # type: ignore[arg-type]

    logger.info("Total nodes to index: %d", len(all_nodes))

    # Index into Qdrant
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection,
    )
    storage_ctx = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex(
        nodes=all_nodes,
        storage_context=storage_ctx,
        embed_model=embed_model,
        show_progress=False,
    )

    logger.info("Ingestion complete for project %s (%d nodes)", project_id, len(all_nodes))
    return len(all_nodes)
