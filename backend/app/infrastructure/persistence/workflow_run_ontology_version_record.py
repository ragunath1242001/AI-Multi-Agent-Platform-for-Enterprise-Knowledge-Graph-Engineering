from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class WorkflowRunOntologyVersionRecord(Base):
    __tablename__ = "workflow_run_ontology_versions"

    workflow_run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflow_runs.id"),
        primary_key=True,
    )
    ontology_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ontology_versions.id"),
        primary_key=True,
    )
