from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hackradar.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from hackradar.models.project import Project


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    project_categories: Mapped[list["ProjectCategory"]] = relationship(
        "ProjectCategory", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"


class ProjectCategory(Base):
    """Many-to-many join between Project and Category."""

    __tablename__ = "project_categories"

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), primary_key=True
    )
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("categories.id"), primary_key=True
    )

    project: Mapped["Project"] = relationship("Project", back_populates="project_categories")
    category: Mapped["Category"] = relationship("Category", back_populates="project_categories")
