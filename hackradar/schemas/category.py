from datetime import datetime

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CategorizationRequest(BaseModel):
    project_ids: list[str]
    categories: list[str] | None = None  # None = auto-discover


class ProjectCategoryAssignment(BaseModel):
    project_id: str
    project_name: str
    category: str


class CategorizationResponse(BaseModel):
    assignments: list[ProjectCategoryAssignment]
    categories_created: list[str]
