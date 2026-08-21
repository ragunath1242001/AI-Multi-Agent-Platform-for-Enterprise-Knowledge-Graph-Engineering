import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.domain.models import IngestionRunResult, IngestionStep
from app.infrastructure.persistence.graph_lineage_repository import GraphLineageRepository
from app.infrastructure.persistence.ontology_version_repository import OntologyVersionRepository
from app.infrastructure.persistence.workflow_run_ontology_version_record import (
    WorkflowRunOntologyVersionRecord,
)
from app.infrastructure.persistence.workflow_run_record import WorkflowRunRecord


class WorkflowRunRepository:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._lineage = GraphLineageRepository(session)
        self._ontology_versions = OntologyVersionRepository(session)

    def create_started(self, dataset_key: str, graph_name: str) -> IngestionRunResult:
        record = WorkflowRunRecord(
            dataset_key=dataset_key,
            graph_name=graph_name,
            status="running",
            steps_json=json.dumps([]),
        )
        self._session.add(record)
        self._session.commit()
        self._session.refresh(record)
        return self._to_result(record)

    def complete(
        self,
        run_id: UUID,
        steps: list[IngestionStep],
        validation_report_id: UUID,
        triple_count: int,
        source_uri: str,
        source_checksum: str,
        graph_iri: str,
    ) -> IngestionRunResult:
        record = self._get(run_id)
        record.status = "completed"
        record.steps_json = json.dumps([step.model_dump() for step in steps])
        record.validation_report_id = str(validation_report_id)
        record.triple_count = triple_count
        record.error = None
        record.updated_at = datetime.now(UTC)
        self._lineage.add(
            workflow_run_id=run_id,
            source_uri=source_uri,
            source_checksum=source_checksum,
            graph_iri=graph_iri,
            triple_count=triple_count,
        )
        self._session.commit()
        self._session.refresh(record)
        return self._to_result(record)

    def link_ontology_versions(self, run_id: UUID, version_ids: list[UUID]) -> None:
        self._session.add_all(
            WorkflowRunOntologyVersionRecord(
                workflow_run_id=str(run_id),
                ontology_version_id=str(version_id),
            )
            for version_id in version_ids
        )
        self._session.commit()

    def fail(self, run_id: UUID, steps: list[IngestionStep], error: str) -> IngestionRunResult:
        record = self._get(run_id)
        record.status = "failed"
        record.steps_json = json.dumps([step.model_dump() for step in steps])
        record.error = error
        record.updated_at = datetime.now(UTC)
        self._session.commit()
        self._session.refresh(record)
        return self._to_result(record)

    def list_recent(self, limit: int = 20) -> list[IngestionRunResult]:
        statement = (
            select(WorkflowRunRecord)
            .order_by(desc(WorkflowRunRecord.created_at))
            .limit(limit)
        )
        return [self._to_result(record) for record in self._session.scalars(statement)]

    def _get(self, run_id: UUID) -> WorkflowRunRecord:
        record = self._session.get(WorkflowRunRecord, str(run_id))
        if record is None:
            raise ValueError(f"Workflow run not found: {run_id}")
        return record

    def _to_result(self, record: WorkflowRunRecord) -> IngestionRunResult:
        steps_payload = json.loads(record.steps_json or "[]")
        # ponytail: recent runs are capped at 20; preload this relation if that limit grows.
        return IngestionRunResult(
            id=UUID(record.id),
            dataset_key=record.dataset_key,
            graph_name=record.graph_name,
            status=record.status,
            steps=[IngestionStep(**step) for step in steps_payload],
            validation_report_id=UUID(record.validation_report_id)
            if record.validation_report_id
            else None,
            ontology_versions=self._ontology_versions.list_for_run(record.id),
            lineage=self._lineage.find_for_run(record.id),
            triple_count=record.triple_count,
            error=record.error,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
