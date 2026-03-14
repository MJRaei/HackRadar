from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from hackradar.db.session import get_db
from hackradar.models.criteria import CriteriaSet
from hackradar.repositories.criteria_repo import CriteriaRepository
from hackradar.schemas.criteria import CriteriaSetCreate, CriteriaSetListResponse, CriteriaSetResponse

router = APIRouter(prefix="/criteria", tags=["criteria"])


def get_criteria_repo(session: AsyncSession = Depends(get_db)) -> CriteriaRepository:
    return CriteriaRepository(session)


@router.post("", response_model=CriteriaSetResponse, status_code=status.HTTP_201_CREATED)
async def create_criteria_set(
    data: CriteriaSetCreate,
    repo: CriteriaRepository = Depends(get_criteria_repo),
) -> CriteriaSetResponse:
    criteria_set = CriteriaSet(
        name=data.name,
        description=data.description,
        criteria=[c.model_dump() for c in data.criteria],
    )
    saved = await repo.save(criteria_set)
    return CriteriaSetResponse.model_validate(saved)


@router.get("", response_model=CriteriaSetListResponse)
async def list_criteria_sets(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    repo: CriteriaRepository = Depends(get_criteria_repo),
) -> CriteriaSetListResponse:
    items = await repo.get_all(offset=offset, limit=limit)
    total = await repo.count()
    return CriteriaSetListResponse(
        items=[CriteriaSetResponse.model_validate(c) for c in items],
        total=total,
    )


@router.get("/{criteria_set_id}", response_model=CriteriaSetResponse)
async def get_criteria_set(
    criteria_set_id: str,
    repo: CriteriaRepository = Depends(get_criteria_repo),
) -> CriteriaSetResponse:
    cs = await repo.get(criteria_set_id)
    if not cs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Criteria set not found")
    return CriteriaSetResponse.model_validate(cs)


@router.delete("/{criteria_set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_criteria_set(
    criteria_set_id: str,
    repo: CriteriaRepository = Depends(get_criteria_repo),
) -> None:
    cs = await repo.get(criteria_set_id)
    if not cs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Criteria set not found")
    await repo.delete(cs)
