import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from hackradar.api.deps import get_categorization_service, get_scoring_service
from hackradar.schemas.category import CategorizationRequest, CategorizationResponse
from hackradar.schemas.score import RankedProjectResponse, ScoreRequest, ScoreResponse
from hackradar.services.categorization_service import CategorizationService
from hackradar.services.scoring_service import ScoringService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/judge", tags=["judging"])


@router.post("/score", response_model=list[ScoreResponse])
async def score_projects(
    data: ScoreRequest,
    scoring_service: ScoringService = Depends(get_scoring_service),
) -> list[ScoreResponse]:
    """
    Score one or more projects against a criteria set.

    The scoring agent queries each project's indexed codebase via RAG,
    evaluates each criterion, and persists the results.
    This is a synchronous (blocking) endpoint — scoring may take several minutes.
    """
    if not data.project_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="project_ids must not be empty",
        )

    try:
        scores = await scoring_service.score_projects(
            project_ids=data.project_ids,
            criteria_set_id=data.criteria_set_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return [ScoreResponse.model_validate(s) for s in scores]


@router.get("/score/{project_id}", response_model=list[ScoreResponse])
async def get_project_scores(
    project_id: str,
    scoring_service: ScoringService = Depends(get_scoring_service),
) -> list[ScoreResponse]:
    """Retrieve all scores for a project across all criteria sets."""
    scores = await scoring_service._score_repo.get_by_project(project_id)
    return [ScoreResponse.model_validate(s) for s in scores]


@router.get("/rankings", response_model=list[RankedProjectResponse])
async def get_rankings(
    criteria_set_id: str = Query(..., description="ID of the criteria set to rank by"),
    scoring_service: ScoringService = Depends(get_scoring_service),
) -> list[RankedProjectResponse]:
    """Return all projects ranked by overall score for a given criteria set."""
    try:
        rankings = await scoring_service.get_rankings(criteria_set_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    return [RankedProjectResponse(**r) for r in rankings]


@router.post("/categorize", response_model=CategorizationResponse)
async def categorize_projects(
    data: CategorizationRequest,
    categorization_service: CategorizationService = Depends(get_categorization_service),
) -> CategorizationResponse:
    """
    Categorize projects by their summaries and README content.

    If `categories` is provided, projects are assigned to the closest matching
    category. If omitted, the agent auto-discovers meaningful clusters.
    """
    if not data.project_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="project_ids must not be empty",
        )

    try:
        result = await categorization_service.categorize(
            project_ids=data.project_ids,
            categories=data.categories,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return result
