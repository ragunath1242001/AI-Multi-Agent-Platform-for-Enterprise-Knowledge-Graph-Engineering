from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.domain.models import GraphLineageSummary
from app.infrastructure.persistence.graph_lineage_record import GraphLineageRecord
from app.infrastructure.persistence.ontology_version_repository import OntologyVersionRepository
from app.infrastructure.persistence.workflow_run_record import WorkflowRunRecord


class GraphLineageRepository:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._ontology_versions = OntologyVersionRepository(session)

    def add(
        self,
        *,
        workflow_run_id: UUID,
        source_uri: str,
        source_checksum: str,
        graph_iri: str,
        triple_count: int,
    ) -> None:
        self._session.add(
            GraphLineageRecord(
                workflow_run_id=str(workflow_run_id),
                source_uri=source_uri,
                source_checksum=source_checksum,
                graph_iri=graph_iri,
                triple_count=triple_count,
            )
        )

    def find_for_run(self, run_id: str) -> GraphLineageSummary | None:
        statement = (
            select(GraphLineageRecord, WorkflowRunRecord)
            .join(WorkflowRunRecord, WorkflowRunRecord.id == GraphLineageRecord.workflow_run_id)
            .where(GraphLineageRecord.workflow_run_id == run_id)
        )
        row = self._session.execute(statement).one_or_none()
        return self._to_summary(*row) if row else None

    def list_for_graph(self, graph_name: str, limit: int = 20) -> list[GraphLineageSummary]:
        statement = (
            select(GraphLineageRecord, WorkflowRunRecord)
            .join(WorkflowRunRecord, WorkflowRunRecord.id == GraphLineageRecord.workflow_run_id)
            .where(WorkflowRunRecord.graph_name == graph_name)
            .order_by(desc(GraphLineageRecord.promoted_at))
            .limit(limit)
        )
        # ponytail: lineage is capped at 20; preload ontology links if that limit grows.
        return [self._to_summary(*row) for row in self._session.execute(statement)]

    def _to_summary(
        self,
        lineage: GraphLineageRecord,
        run: WorkflowRunRecord,
    ) -> GraphLineageSummary:
        if run.validation_report_id is None:
            raise ValueError(f"Lineage run has no validation report: {run.id}")
        return GraphLineageSummary(
            workflow_run_id=UUID(run.id),
            dataset_key=run.dataset_key,
            graph_name=run.graph_name,
            source_uri=lineage.source_uri,
            source_checksum=lineage.source_checksum,
            validation_report_id=UUID(run.validation_report_id),
            ontology_versions=self._ontology_versions.list_for_run(run.id),
            graph_iri=lineage.graph_iri,
            triple_count=lineage.triple_count,
            promoted_at=lineage.promoted_at,
        )
