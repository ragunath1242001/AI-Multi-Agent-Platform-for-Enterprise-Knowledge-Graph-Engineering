from dataclasses import dataclass
from pathlib import Path

from app.domain.models import IngestionDatasetSummary, IngestionRunResult, IngestionStep
from app.infrastructure.persistence.validation_report_repository import ValidationReportRepository
from app.infrastructure.persistence.workflow_run_repository import WorkflowRunRepository
from app.services.graph_store_service import GraphStoreService
from app.services.validation_service import ValidationService


@dataclass(frozen=True)
class IngestionDatasetDefinition:
    key: str
    graph_name: str
    title: str
    relative_path: str


DATASETS = [
    IngestionDatasetDefinition(
        key="synthetic-medical-cohort",
        graph_name="synthetic-medical-cohort",
        title="Synthetic Medical Cohort",
        relative_path="examples/synthetic-medical-cohort.ttl",
    ),
    IngestionDatasetDefinition(
        key="uci-heart-disease-cleveland",
        graph_name="uci-heart-disease-cleveland",
        title="UCI Heart Disease Cleveland",
        relative_path="examples/uci-heart-disease-cleveland.ttl",
    ),
    IngestionDatasetDefinition(
        key="semanticops-medical-ontology",
        graph_name="semanticops-medical-ontology",
        title="SemanticOps Medical Ontology",
        relative_path="ontologies/semanticops-medical.ttl",
    ),
]


class IngestionWorkflowService:
    def __init__(
        self,
        assets_dir: Path,
        run_repository: WorkflowRunRepository,
        validation_repository: ValidationReportRepository,
        graph_store_service: GraphStoreService,
    ) -> None:
        self._assets_dir = assets_dir
        self._run_repository = run_repository
        self._validation_service = ValidationService(validation_repository)
        self._graph_store_service = graph_store_service

    def list_datasets(self) -> list[IngestionDatasetSummary]:
        return [
            IngestionDatasetSummary(
                key=dataset.key,
                graph_name=dataset.graph_name,
                title=dataset.title,
                path=dataset.relative_path,
            )
            for dataset in DATASETS
        ]

    def list_runs(self) -> list[IngestionRunResult]:
        return self._run_repository.list_recent()

    async def run(self, dataset_key: str) -> IngestionRunResult:
        dataset = self._dataset(dataset_key)
        run = self._run_repository.create_started(
            dataset_key=dataset.key,
            graph_name=dataset.graph_name,
        )
        steps: list[IngestionStep] = []

        try:
            data_graph_ttl = self._read_asset(dataset.relative_path)
            steps.append(
                IngestionStep(
                    name="ingest",
                    status="completed",
                    detail=f"Loaded {dataset.relative_path}.",
                )
            )

            shapes_ttl = self._read_shapes()
            validation = self._validation_service.validate(
                graph_name=dataset.graph_name,
                data_graph_ttl=data_graph_ttl,
                shacl_shapes_ttl=shapes_ttl,
            )
            steps.append(
                IngestionStep(
                    name="validate",
                    status="completed" if validation.conforms else "failed",
                    detail="SHACL conforms." if validation.conforms else validation.report_text,
                )
            )
            if not validation.conforms:
                return self._run_repository.fail(run.id, steps, validation.report_text)

            promotion = await self._graph_store_service.upsert_graph(
                graph_name=dataset.graph_name,
                data_graph_ttl=data_graph_ttl,
            )
            steps.append(
                IngestionStep(
                    name="promote",
                    status="completed",
                    detail=f"Promoted {promotion.triple_count} triples to {promotion.graph_iri}.",
                )
            )

            steps.append(
                IngestionStep(
                    name="query_ready",
                    status="completed",
                    detail="Named graph is available for SPARQL queries.",
                )
            )
            return self._run_repository.complete(
                run_id=run.id,
                steps=steps,
                validation_report_id=validation.id,
                triple_count=promotion.triple_count,
            )
        except Exception as exc:
            steps.append(IngestionStep(name="error", status="failed", detail=str(exc)))
            return self._run_repository.fail(run.id, steps, str(exc))

    def _dataset(self, dataset_key: str) -> IngestionDatasetDefinition:
        for dataset in DATASETS:
            if dataset.key == dataset_key:
                return dataset
        raise ValueError(f"Unknown ingestion dataset: {dataset_key}")

    def _read_asset(self, relative_path: str) -> str:
        path = (self._assets_dir / relative_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Knowledge asset not found: {path}")
        return path.read_text(encoding="utf-8-sig")

    def _read_shapes(self) -> str:
        core_shapes = self._read_asset("shapes/semanticops-core.shacl.ttl")
        medical_shapes = self._read_asset("shapes/semanticops-medical.shacl.ttl")
        return f"{core_shapes}\n{medical_shapes}"
