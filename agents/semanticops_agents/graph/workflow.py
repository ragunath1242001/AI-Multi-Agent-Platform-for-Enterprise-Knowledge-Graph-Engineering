from functools import partial

from langgraph.graph import END, StateGraph

from semanticops_agents.nodes import (
    observability_agent,
    ontology_agent,
    promotion_agent,
    rdf_generation_agent,
    validation_agent,
)
from semanticops_agents.state import (
    GraphEngineeringState,
    PromotionOperation,
    ValidationOperation,
)


def _continue_or_observe(state: GraphEngineeringState) -> str:
    return "observe" if state.get("error") else "continue"


def _promote_or_observe(state: GraphEngineeringState) -> str:
    return "promote" if state.get("validation_conforms") and not state.get("error") else "observe"


def build_graph_engineering_workflow(
    *,
    validate_graph: ValidationOperation,
    promote_graph: PromotionOperation,
):
    workflow = StateGraph(GraphEngineeringState)
    workflow.add_node("ontology", ontology_agent)
    workflow.add_node("rdf_generation", rdf_generation_agent)
    workflow.add_node("validation", partial(validation_agent, validate_graph=validate_graph))
    workflow.add_node("promotion", partial(promotion_agent, promote_graph=promote_graph))
    workflow.add_node("observability", observability_agent)

    workflow.set_entry_point("ontology")
    workflow.add_conditional_edges(
        "ontology",
        _continue_or_observe,
        {"continue": "rdf_generation", "observe": "observability"},
    )
    workflow.add_conditional_edges(
        "rdf_generation",
        _continue_or_observe,
        {"continue": "validation", "observe": "observability"},
    )
    workflow.add_conditional_edges(
        "validation",
        _promote_or_observe,
        {"promote": "promotion", "observe": "observability"},
    )
    workflow.add_edge("promotion", "observability")
    workflow.add_edge("observability", END)
    return workflow.compile()
