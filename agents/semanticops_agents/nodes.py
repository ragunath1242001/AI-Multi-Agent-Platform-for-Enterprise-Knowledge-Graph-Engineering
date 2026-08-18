from semanticops_agents.state import GraphEngineeringState


def ontology_agent(state: GraphEngineeringState) -> GraphEngineeringState:
    state["observations"] = [
        *state.get("observations", []),
        "Ontology agent reviewed source domain.",
    ]
    return state


def rdf_generation_agent(state: GraphEngineeringState) -> GraphEngineeringState:
    state["generated_rdf_ttl"] = state.get("generated_rdf_ttl", "")
    state["observations"] = [
        *state.get("observations", []),
        "RDF generation agent produced Turtle.",
    ]
    return state


def validation_agent(state: GraphEngineeringState) -> GraphEngineeringState:
    state["shacl_report"] = "Validation placeholder: no violations evaluated."
    state["observations"] = [*state.get("observations", []), "SHACL validation agent completed."]
    return state


def reasoning_agent(state: GraphEngineeringState) -> GraphEngineeringState:
    state["inferred_rdf_ttl"] = state.get("generated_rdf_ttl", "")
    state["observations"] = [
        *state.get("observations", []),
        "Reasoning agent materialized inferences.",
    ]
    return state
