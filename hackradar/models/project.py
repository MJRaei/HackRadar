from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hackradar.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from hackradar.models.category import ProjectCategory
    from hackradar.models.score import Score


class ProjectStatus:
    PENDING = "pending"
    CLONING = "cloning"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    github_url: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    readme: Mapped[str | None] = mapped_column(Text, nullable=True)
    local_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=ProjectStatus.PENDING)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    scores: Mapped[list["Score"]] = relationship("Score", back_populates="project", cascade="all, delete-orphan")
    project_categories: Mapped[list["ProjectCategory"]] = relationship(
        "ProjectCategory", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r} status={self.status}>"
