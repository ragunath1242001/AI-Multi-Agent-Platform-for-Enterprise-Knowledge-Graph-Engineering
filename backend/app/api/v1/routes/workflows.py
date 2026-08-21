from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.routes.knowledge_graphs import get_graph_store_service
from app.core.settings import get_settings
from app.domain.models import IngestionDatasetSummary, IngestionRunRequest, IngestionRunResult
from app.infrastructure.database import get_session
from app.infrastructure.persistence.ontology_version_repository import OntologyVersionRepository
from app.infrastructure.persistence.validation_report_repository import ValidationReportRepository
from app.infrastructure.persistence.workflow_run_repository import WorkflowRunRepository
from app.services.graph_store_service import GraphStoreService
from app.services.ingestion_workflow_service import IngestionWorkflowService

router = APIRouter()

SessionDependency = Annotated[Session, Depends(get_session)]


def get_ingestion_workflow_service(
    session: SessionDependency,
    graph_store_service: Annotated[GraphStoreService, Depends(get_graph_store_service)],
) -> IngestionWorkflowService:
    return IngestionWorkflowService(
        assets_dir=Path(get_settings().knowledge_assets_dir),
        run_repository=WorkflowRunRepository(session),
        ontology_version_repository=OntologyVersionRepository(session),
        validation_repository=ValidationReportRepository(session),
        graph_store_service=graph_store_service,
    )


@router.get("/ingestion/datasets", response_model=list[IngestionDatasetSummary])
async def list_ingestion_datasets(
    service: Annotated[IngestionWorkflowService, Depends(get_ingestion_workflow_service)],
) -> list[IngestionDatasetSummary]:
    return service.list_datasets()


@router.post("/ingestion/runs", response_model=IngestionRunResult)
async def start_ingestion_run(
    request: IngestionRunRequest,
    service: Annotated[IngestionWorkflowService, Depends(get_ingestion_workflow_service)],
) -> IngestionRunResult:
    try:
        return await service.run(request.dataset_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/ingestion/runs", response_model=list[IngestionRunResult])
async def list_ingestion_runs(
    service: Annotated[IngestionWorkflowService, Depends(get_ingestion_workflow_service)],
) -> list[IngestionRunResult]:
    return service.list_runs()
