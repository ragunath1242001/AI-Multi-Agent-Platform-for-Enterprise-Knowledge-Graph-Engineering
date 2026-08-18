from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GraphValidationRequest(BaseModel):
    graph_name: str = Field(default="default", min_length=1, max_length=120)
    data_graph_ttl: str = Field(..., description="RDF data graph serialized as Turtle.")
    shacl_shapes_ttl: str = Field(..., description="SHACL shapes graph serialized as Turtle.")


class GraphValidationResult(BaseModel):
    id: UUID
    graph_name: str
    conforms: bool
    report_text: str
    created_at: datetime


class GraphValidationReportSummary(BaseModel):
    id: UUID
    graph_name: str
    conforms: bool
    created_at: datetime


class GraphUpsertRequest(BaseModel):
    graph_name: str = Field(..., min_length=1, max_length=120)
    data_graph_ttl: str = Field(..., description="Approved RDF graph serialized as Turtle.")


class GraphStoreResult(BaseModel):
    graph_name: str
    graph_iri: str
    triple_count: int


class GraphSummary(BaseModel):
    graph_iri: str
    graph_name: str


class SparqlQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)


class SparqlQueryResult(BaseModel):
    results: dict


class IngestionDatasetSummary(BaseModel):
    key: str
    graph_name: str
    title: str
    path: str


class IngestionRunRequest(BaseModel):
    dataset_key: str = Field(..., min_length=1)


class IngestionStep(BaseModel):
    name: str
    status: str
    detail: str


class IngestionRunResult(BaseModel):
    id: UUID
    dataset_key: str
    graph_name: str
    status: str
    steps: list[IngestionStep]
    validation_report_id: UUID | None = None
    triple_count: int | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
