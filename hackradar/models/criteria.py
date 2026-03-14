from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hackradar.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from hackradar.models.score import Score


class CriteriaSet(Base, TimestampMixin):
    """
    A named set of judging criteria.

    `criteria` is stored as a JSON list of objects:
    [
        {"name": "Innovation", "description": "How novel is the idea?", "weight": 0.3},
        {"name": "Technical", "description": "Code quality and complexity", "weight": 0.4},
        ...
    ]
    Weights should sum to 1.0 but are not enforced at the DB level.
    """

    __tablename__ = "criteria_sets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    scores: Mapped[list["Score"]] = relationship(
        "Score", back_populates="criteria_set", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CriteriaSet id={self.id} name={self.name!r}>"
