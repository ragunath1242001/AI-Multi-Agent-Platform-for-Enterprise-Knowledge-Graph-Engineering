from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.models import OntologyVersionSummary
from app.infrastructure.persistence.ontology_version_record import OntologyVersionRecord
from app.infrastructure.persistence.workflow_run_ontology_version_record import (
    WorkflowRunOntologyVersionRecord,
)


class OntologyVersionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find(self, ontology_key: str, checksum: str) -> OntologyVersionSummary | None:
        statement = select(OntologyVersionRecord).where(
            OntologyVersionRecord.ontology_key == ontology_key,
            OntologyVersionRecord.checksum == checksum,
        )
        record = self._session.scalar(statement)
        return self._to_summary(record) if record else None

    def create_or_get(
        self,
        *,
        ontology_key: str,
        title: str,
        path: str,
        namespace: str,
        version: str | None,
        checksum: str,
        graph_iri: str,
        triple_count: int,
    ) -> OntologyVersionSummary:
        record = OntologyVersionRecord(
            ontology_key=ontology_key,
            title=title,
            path=path,
            namespace=namespace,
            version=version,
            checksum=checksum,
            graph_iri=graph_iri,
            triple_count=triple_count,
        )
        self._session.add(record)
        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            existing = self.find(ontology_key, checksum)
            if existing is None:
                raise
            return existing
        self._session.refresh(record)
        return self._to_summary(record)

    def list_recent(self, limit: int = 100) -> list[OntologyVersionSummary]:
        statement = (
            select(OntologyVersionRecord)
            .order_by(desc(OntologyVersionRecord.created_at))
            .limit(limit)
        )
        return [self._to_summary(record) for record in self._session.scalars(statement)]

    def list_for_run(self, run_id: str) -> list[OntologyVersionSummary]:
        statement = (
            select(OntologyVersionRecord)
            .join(
                WorkflowRunOntologyVersionRecord,
                WorkflowRunOntologyVersionRecord.ontology_version_id
                == OntologyVersionRecord.id,
            )
            .where(WorkflowRunOntologyVersionRecord.workflow_run_id == run_id)
            .order_by(OntologyVersionRecord.ontology_key)
        )
        return [self._to_summary(record) for record in self._session.scalars(statement)]

    @staticmethod
    def _to_summary(record: OntologyVersionRecord) -> OntologyVersionSummary:
        return OntologyVersionSummary(
            id=UUID(record.id),
            ontology_key=record.ontology_key,
            title=record.title,
            path=record.path,
            namespace=record.namespace,
            version=record.version,
            checksum=record.checksum,
            graph_iri=record.graph_iri,
            triple_count=record.triple_count,
            created_at=record.created_at,
        )
