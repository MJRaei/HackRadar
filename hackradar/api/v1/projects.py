import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status

from hackradar.api.deps import get_bulk_upload_service, get_ingestion_service, get_project_service
from hackradar.schemas.project import BulkUploadResponse, BulkUploadSkipped, ProjectCreate, ProjectListResponse, ProjectResponse
from hackradar.services.bulk_upload import BulkUploadService
from hackradar.services.ingestion_service import IngestionService
from hackradar.services.project_service import ProjectService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_project(
    data: ProjectCreate,
    background_tasks: BackgroundTasks,
    project_service: ProjectService = Depends(get_project_service),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> ProjectResponse:
    """
    Submit a new hackathon project.

    The project record is created immediately (status=pending).
    Repository cloning and RAG indexing run in the background.
    Poll GET /projects/{id} to check indexing status.
    """
    try:
        project = await project_service.create(data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    background_tasks.add_task(
        project_service.clone_and_index,
        project_id=project.id,
        ingestion_service=ingestion_service,
    )

    return ProjectResponse.model_validate(project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectListResponse:
    items, total = await project_service.list_all(offset=offset, limit=limit)
    return ProjectListResponse(
        items=[ProjectResponse.model_validate(p) for p in items],
        total=total,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    project = await project_service.get(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectResponse.model_validate(project)


_ALLOWED_EXTENSIONS = {".txt", ".csv"}
_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post(
    "/bulk-upload",
    response_model=BulkUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def bulk_upload_projects(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    bulk_upload_service: BulkUploadService = Depends(get_bulk_upload_service),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> BulkUploadResponse:
    """
    Upload a .txt or .csv file containing GitHub repository URLs.

    Each URL found in the file is queued as a new project (status=pending).
    Duplicate URLs are skipped and reported in the response.
    """
    extension = Path(file.filename or "").suffix.lower()
    if extension not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type '{extension}'. Upload a .txt or .csv file.",
        )

    raw = await file.read()
    if len(raw) > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the 5 MB limit.",
        )

    try:
        content = raw.decode("utf-8", errors="replace")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not read file: {exc}",
        )

    result = await bulk_upload_service.process(
        file_content=content,
        file_extension=extension,
        background_tasks=background_tasks,
        ingestion_service=ingestion_service,
    )

    return BulkUploadResponse(
        queued=[ProjectResponse.model_validate(p) for p in result.queued],
        skipped=[BulkUploadSkipped(url=s.url, reason=s.reason) for s in result.skipped],
        total_found=result.total_found,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> None:
    try:
        await project_service.delete(project_id)
        await ingestion_service.delete_collection(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
