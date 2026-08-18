from typing import TypedDict


class GraphEngineeringState(TypedDict, total=False):
    source_text: str
    ontology_ttl: str
    generated_rdf_ttl: str
    shacl_report: str
    inferred_rdf_ttl: str
    observations: list[str]

