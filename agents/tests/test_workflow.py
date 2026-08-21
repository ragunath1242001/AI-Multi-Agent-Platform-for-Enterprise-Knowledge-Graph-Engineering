import asyncio

from semanticops_agents.graph.workflow import build_graph_engineering_workflow
from semanticops_agents.state import PromotionOutcome, ValidationOutcome


def test_workflow_runs() -> None:
    promotions: list[str] = []

    def validate_graph(_: str, data_graph_ttl: str, __: str) -> ValidationOutcome:
        return ValidationOutcome("report-1", "ex:asset" in data_graph_ttl, "SHACL violations")

    async def promote_graph(graph_name: str, _: str) -> PromotionOutcome:
        promotions.append(graph_name)
        return PromotionOutcome(f"https://semanticops.ai/graphs/{graph_name}", 1)

    graph = build_graph_engineering_workflow(
        validate_graph=validate_graph,
        promote_graph=promote_graph,
    )
    base_state = {
        "graph_name": "sample",
        "source_path": "examples/sample.ttl",
        "ontology_ttl": (
            "@prefix owl: <http://www.w3.org/2002/07/owl#> . "
            "@prefix ex: <https://example.com/> . ex:Asset a owl:Class ."
        ),
        "shacl_shapes_ttl": "",
    }

    result = asyncio.run(
        graph.ainvoke(
            {
                **base_state,
                "source_text": "@prefix ex: <https://example.com/> . ex:asset a ex:Asset .",
            }
        )
    )
    assert [step["name"] for step in result["steps"]] == [
        "ontology",
        "rdf_generation",
        "validation",
        "promotion",
        "observability",
    ]
    assert promotions == ["sample"]

    failed = asyncio.run(
        graph.ainvoke(
            {
                **base_state,
                "source_text": "@prefix ex: <https://example.com/> . ex:invalid a ex:Asset .",
            }
        )
    )
    assert [step["name"] for step in failed["steps"]] == [
        "ontology",
        "rdf_generation",
        "validation",
        "observability",
    ]
    assert promotions == ["sample"]
