from datetime import datetime

from pydantic import BaseModel, field_validator


class Criterion(BaseModel):
    """A single judging criterion within a criteria set."""

    name: str
    description: str
    weight: float = 1.0

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("weight must be positive")
        return v


class CriteriaSetCreate(BaseModel):
    name: str
    description: str | None = None
    criteria: list[Criterion]

    @field_validator("criteria")
    @classmethod
    def validate_criteria_not_empty(cls, v: list[Criterion]) -> list[Criterion]:
        if not v:
            raise ValueError("criteria list must not be empty")
        return v


class CriteriaSetResponse(BaseModel):
    id: str
    name: str
    description: str | None
    criteria: list[Criterion]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CriteriaSetListResponse(BaseModel):
    items: list[CriteriaSetResponse]
    total: int
