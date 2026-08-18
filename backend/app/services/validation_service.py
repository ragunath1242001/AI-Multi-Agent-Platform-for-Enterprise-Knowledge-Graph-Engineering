from pyshacl import validate
from rdflib import Graph

from app.domain.models import GraphValidationReportSummary, GraphValidationResult
from app.infrastructure.persistence.validation_report_repository import ValidationReportRepository


class ValidationService:
    def __init__(self, repository: ValidationReportRepository) -> None:
        self._repository = repository

    def validate(
        self,
        graph_name: str,
        data_graph_ttl: str,
        shacl_shapes_ttl: str,
    ) -> GraphValidationResult:
        data_graph = Graph()
        shapes_graph = Graph()
        data_graph.parse(data=data_graph_ttl, format="turtle")
        shapes_graph.parse(data=shacl_shapes_ttl, format="turtle")

        conforms, _, report_text = validate(
            data_graph=data_graph,
            shacl_graph=shapes_graph,
            inference="rdfs",
            serialize_report_graph=False,
        )
        return self._repository.create(
            graph_name=graph_name,
            conforms=bool(conforms),
            report_text=str(report_text),
        )

    def list_reports(self, limit: int = 20) -> list[GraphValidationReportSummary]:
        return self._repository.list_recent(limit=limit)


def get_validation_service() -> ValidationService:
    raise RuntimeError("ValidationService must be created by the API dependency layer.")
