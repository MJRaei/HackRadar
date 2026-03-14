from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hackradar.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from hackradar.models.criteria import CriteriaSet
    from hackradar.models.project import Project


class Score(Base, TimestampMixin):
    """
    Scoring result for one project against one criteria set.

    `criterion_scores` is a JSON dict:
    {
        "Innovation": {"score": 8, "rationale": "..."},
        "Technical":  {"score": 7, "rationale": "..."},
        ...
    }
    """

    __tablename__ = "scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    criteria_set_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("criteria_sets.id"), nullable=False
    )
    criterion_scores: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="scores")
    criteria_set: Mapped["CriteriaSet"] = relationship("CriteriaSet", back_populates="scores")

    def __repr__(self) -> str:
        return f"<Score id={self.id} project_id={self.project_id} overall={self.overall_score}>"
