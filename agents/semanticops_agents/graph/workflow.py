from langgraph.graph import END, StateGraph

from semanticops_agents.nodes import (
    ontology_agent,
    rdf_generation_agent,
    reasoning_agent,
    validation_agent,
)
from semanticops_agents.state import GraphEngineeringState


def build_graph_engineering_workflow():
    workflow = StateGraph(GraphEngineeringState)
    workflow.add_node("ontology", ontology_agent)
    workflow.add_node("rdf_generation", rdf_generation_agent)
    workflow.add_node("validation", validation_agent)
    workflow.add_node("reasoning", reasoning_agent)

    workflow.set_entry_point("ontology")
    workflow.add_edge("ontology", "rdf_generation")
    workflow.add_edge("rdf_generation", "validation")
    workflow.add_edge("validation", "reasoning")
    workflow.add_edge("reasoning", END)
    return workflow.compile()

