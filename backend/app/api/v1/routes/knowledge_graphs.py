from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException
from rdflib.plugins.parsers.notation3 import BadSyntax
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.domain.models import (
    GraphStoreResult,
    GraphSummary,
    GraphUpsertRequest,
    GraphValidationReportSummary,
    GraphValidationRequest,
    GraphValidationResult,
    SparqlQueryRequest,
    SparqlQueryResult,
)
from app.infrastructure.database import get_session
from app.infrastructure.graph.fuseki_client import FusekiClient
from app.infrastructure.persistence.validation_report_repository import ValidationReportRepository
from app.services.graph_store_service import GraphStoreService
from app.services.validation_service import ValidationService

router = APIRouter()


SessionDependency = Annotated[Session, Depends(get_session)]


def get_validation_service(session: SessionDependency) -> ValidationService:
    return ValidationService(ValidationReportRepository(session))


def get_graph_store_service() -> GraphStoreService:
    settings = get_settings()
    return GraphStoreService(
        FusekiClient(
            endpoint_url=str(settings.fuseki_url).rstrip("/"),
            username=settings.fuseki_user,
            password=settings.fuseki_password,
        )
    )


@router.post("/validate", response_model=GraphValidationResult)
async def validate_graph(
    request: GraphValidationRequest,
    service: Annotated[ValidationService, Depends(get_validation_service)],
) -> GraphValidationResult:
    try:
        return service.validate(
            graph_name=request.graph_name,
            data_graph_ttl=request.data_graph_ttl,
            shacl_shapes_ttl=request.shacl_shapes_ttl,
        )
    except BadSyntax as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Turtle input: {exc}") from exc


@router.get("/validation-reports", response_model=list[GraphValidationReportSummary])
async def list_validation_reports(
    service: Annotated[ValidationService, Depends(get_validation_service)],
) -> list[GraphValidationReportSummary]:
    return service.list_reports()


@router.put("/graphs", response_model=GraphStoreResult)
async def upsert_graph(
    request: GraphUpsertRequest,
    service: Annotated[GraphStoreService, Depends(get_graph_store_service)],
) -> GraphStoreResult:
    try:
        return await service.upsert_graph(
            graph_name=request.graph_name,
            data_graph_ttl=request.data_graph_ttl,
        )
    except BadSyntax as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Turtle input: {exc}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Graph store write failed.") from exc


@router.get("/graphs", response_model=list[GraphSummary])
async def list_graphs(
    service: Annotated[GraphStoreService, Depends(get_graph_store_service)],
) -> list[GraphSummary]:
    try:
        return await service.list_graphs()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Graph store list failed.") from exc


@router.post("/query", response_model=SparqlQueryResult)
async def execute_sparql_query(
    request: SparqlQueryRequest,
    service: Annotated[GraphStoreService, Depends(get_graph_store_service)],
) -> SparqlQueryResult:
    try:
        return await service.execute_query(request.query)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Graph store query failed.") from exc
