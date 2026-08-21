from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal, TypedDict


class AgentStep(TypedDict):
    name: str
    status: Literal["completed", "failed"]
    detail: str


@dataclass(frozen=True)
class ValidationOutcome:
    report_id: str
    conforms: bool
    report_text: str


@dataclass(frozen=True)
class PromotionOutcome:
    graph_iri: str
    triple_count: int


ValidationOperation = Callable[[str, str, str], ValidationOutcome]
PromotionOperation = Callable[[str, str], Awaitable[PromotionOutcome]]


class GraphEngineeringState(TypedDict, total=False):
    graph_name: str
    source_path: str
    source_text: str
    ontology_ttl: str
    shacl_shapes_ttl: str
    generated_rdf_ttl: str
    shacl_report: str
    validation_report_id: str
    validation_conforms: bool
    graph_iri: str
    triple_count: int
    error: str
    steps: list[AgentStep]
    observations: list[str]
