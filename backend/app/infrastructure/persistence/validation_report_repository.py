from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.domain.models import GraphValidationReportSummary, GraphValidationResult
from app.infrastructure.persistence.validation_report_record import ValidationReportRecord


class ValidationReportRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, graph_name: str, conforms: bool, report_text: str) -> GraphValidationResult:
        record = ValidationReportRecord(
            graph_name=graph_name,
            conforms=conforms,
            report_text=report_text,
        )
        self._session.add(record)
        self._session.commit()
        self._session.refresh(record)
        return self._to_result(record)

    def list_recent(self, limit: int = 20) -> list[GraphValidationReportSummary]:
        statement = (
            select(ValidationReportRecord)
            .order_by(desc(ValidationReportRecord.created_at))
            .limit(limit)
        )
        return [self._to_summary(record) for record in self._session.scalars(statement)]

    @staticmethod
    def _to_result(record: ValidationReportRecord) -> GraphValidationResult:
        return GraphValidationResult(
            id=UUID(record.id),
            graph_name=record.graph_name,
            conforms=record.conforms,
            report_text=record.report_text,
            created_at=record.created_at,
        )

    @staticmethod
    def _to_summary(record: ValidationReportRecord) -> GraphValidationReportSummary:
        return GraphValidationReportSummary(
            id=UUID(record.id),
            graph_name=record.graph_name,
            conforms=record.conforms,
            created_at=record.created_at,
        )
