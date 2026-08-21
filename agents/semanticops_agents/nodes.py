from rdflib import Graph
from rdflib.namespace import OWL, RDF

from semanticops_agents.state import GraphEngineeringState, PromotionOperation, ValidationOperation


def _completed(state: GraphEngineeringState, name: str, detail: str) -> dict:
    return {
        "steps": [
            *state.get("steps", []),
            {"name": name, "status": "completed", "detail": detail},
        ],
        "observations": [*state.get("observations", []), detail],
    }


def _failed(state: GraphEngineeringState, name: str, error: Exception) -> dict:
    detail = str(error)
    return {
        "error": detail,
        "steps": [
            *state.get("steps", []),
            {"name": name, "status": "failed", "detail": detail},
        ],
        "observations": [*state.get("observations", []), f"{name} failed: {detail}"],
    }


def ontology_agent(state: GraphEngineeringState) -> dict:
    try:
        ontology = Graph().parse(data=state["ontology_ttl"], format="turtle")
        class_count = len(set(ontology.subjects(RDF.type, OWL.Class)))
        return _completed(
            state,
            "ontology",
            f"Reviewed {len(ontology)} ontology triples and {class_count} OWL classes.",
        )
    except Exception as exc:
        return _failed(state, "ontology", exc)


def rdf_generation_agent(state: GraphEngineeringState) -> dict:
    try:
        graph = Graph().parse(data=state["source_text"], format="turtle")
        detail = f"Prepared {len(graph)} RDF triples from {state['source_path']}."
        return {
            "generated_rdf_ttl": graph.serialize(format="turtle"),
            **_completed(state, "rdf_generation", detail),
        }
    except Exception as exc:
        return _failed(state, "rdf_generation", exc)


def validation_agent(
    state: GraphEngineeringState,
    *,
    validate_graph: ValidationOperation,
) -> dict:
    try:
        outcome = validate_graph(
            state["graph_name"],
            state["generated_rdf_ttl"],
            state["shacl_shapes_ttl"],
        )
        detail = "SHACL conforms." if outcome.conforms else outcome.report_text
        return {
            "validation_report_id": outcome.report_id,
            "validation_conforms": outcome.conforms,
            "shacl_report": outcome.report_text,
            "steps": [
                *state.get("steps", []),
                {
                    "name": "validation",
                    "status": "completed" if outcome.conforms else "failed",
                    "detail": detail,
                },
            ],
            "observations": [*state.get("observations", []), detail],
        }
    except Exception as exc:
        return _failed(state, "validation", exc)


async def promotion_agent(
    state: GraphEngineeringState,
    *,
    promote_graph: PromotionOperation,
) -> dict:
    try:
        outcome = await promote_graph(state["graph_name"], state["generated_rdf_ttl"])
        detail = f"Promoted {outcome.triple_count} triples to {outcome.graph_iri}."
        return {
            "graph_iri": outcome.graph_iri,
            "triple_count": outcome.triple_count,
            **_completed(state, "promotion", detail),
        }
    except Exception as exc:
        return _failed(state, "promotion", exc)


def observability_agent(state: GraphEngineeringState) -> dict:
    if error := state.get("error"):
        detail = f"Recorded workflow failure: {error}"
    elif not state.get("validation_conforms"):
        detail = "Recorded validation failure; graph promotion was skipped."
    else:
        detail = f"Recorded query-ready graph {state['graph_iri']}."
    return _completed(state, "observability", detail)
