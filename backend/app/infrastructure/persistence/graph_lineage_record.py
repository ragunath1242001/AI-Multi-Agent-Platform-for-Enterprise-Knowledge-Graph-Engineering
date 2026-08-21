from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class GraphLineageRecord(Base):
    __tablename__ = "graph_lineage"

    workflow_run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    source_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    source_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    graph_iri: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    triple_count: Mapped[int] = mapped_column(Integer, nullable=False)
    promoted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True,
    )
