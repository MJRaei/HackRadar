"""
FastAPI dependency factories.

All services and infrastructure clients are injected through these
`Depends()` providers, keeping route handlers free of construction logic.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from qdrant_client import QdrantClient
from sqlalchemy.ext.asyncio import AsyncSession

from hackradar.config import Settings, get_settings
from hackradar.db.session import get_db
from hackradar.services.bulk_upload import BulkUploadService
from hackradar.services.categorization_service import CategorizationService
from hackradar.services.ingestion_service import IngestionService
from hackradar.services.project_service import ProjectService
from hackradar.services.scoring_service import ScoringService


def get_qdrant_client(settings: Settings = Depends(get_settings)) -> QdrantClient:
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def get_project_service(session: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(session)


def get_bulk_upload_service(
    project_service: ProjectService = Depends(get_project_service),
) -> BulkUploadService:
    return BulkUploadService(project_service)


def get_ingestion_service(
    qdrant: QdrantClient = Depends(get_qdrant_client),
) -> IngestionService:
    return IngestionService(qdrant)


def get_scoring_service(
    session: AsyncSession = Depends(get_db),
    qdrant: QdrantClient = Depends(get_qdrant_client),
) -> ScoringService:
    return ScoringService(session, qdrant)


def get_categorization_service(
    session: AsyncSession = Depends(get_db),
) -> CategorizationService:
    return CategorizationService(session)
