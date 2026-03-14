from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_validator


class ProjectCreate(BaseModel):
    name: str
    github_url: str
    summary: str | None = None

    @field_validator("github_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        if not v.startswith("https://github.com/"):
            raise ValueError("github_url must start with https://github.com/")
        return v.rstrip("/")


class ProjectResponse(BaseModel):
    id: str
    name: str
    github_url: str
    summary: str | None
    readme: str | None
    local_path: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
