from datetime import datetime

from pydantic import BaseModel


class CriterionScore(BaseModel):
    score: float  # 0.0 – 10.0
    rationale: str


class ScoreRequest(BaseModel):
    project_ids: list[str]
    criteria_set_id: str


class ScoreResponse(BaseModel):
    id: str
    project_id: str
    criteria_set_id: str
    criterion_scores: dict[str, CriterionScore]
    overall_score: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RankedProjectResponse(BaseModel):
    rank: int
    project_id: str
    project_name: str
    overall_score: float | None
    criteria_set_id: str
