from semanticops_agents.graph.workflow import build_graph_engineering_workflow


def test_workflow_runs() -> None:
    graph = build_graph_engineering_workflow()
    result = graph.invoke({"source_text": "Customer owns account."})
    assert "SHACL validation agent completed." in result["observations"]

