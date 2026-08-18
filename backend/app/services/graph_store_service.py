from typing import Protocol

from rdflib import Graph

from app.domain.models import GraphStoreResult, GraphSummary, SparqlQueryResult

GRAPH_IRI_PREFIX = "https://semanticops.ai/graphs/"


class GraphStoreClient(Protocol):
    async def put_graph(self, graph_iri: str, data_graph_ttl: str) -> None: ...

    async def execute_sparql(self, query: str) -> dict: ...

    async def list_graphs(self) -> dict: ...


class GraphStoreService:
    def __init__(self, client: GraphStoreClient) -> None:
        self._client = client

    async def upsert_graph(self, graph_name: str, data_graph_ttl: str) -> GraphStoreResult:
        parsed_graph = Graph()
        parsed_graph.parse(data=data_graph_ttl, format="turtle")
        graph_iri = graph_name_to_iri(graph_name)

        await self._client.put_graph(graph_iri=graph_iri, data_graph_ttl=data_graph_ttl)
        return GraphStoreResult(
            graph_name=graph_name,
            graph_iri=graph_iri,
            triple_count=len(parsed_graph),
        )

    async def list_graphs(self) -> list[GraphSummary]:
        payload = await self._client.list_graphs()
        bindings = payload.get("results", {}).get("bindings", [])
        return [
            GraphSummary(
                graph_iri=binding["graph"]["value"],
                graph_name=iri_to_graph_name(binding["graph"]["value"]),
            )
            for binding in bindings
            if "graph" in binding
        ]

    async def execute_query(self, query: str) -> SparqlQueryResult:
        return SparqlQueryResult(results=await self._client.execute_sparql(query))


def graph_name_to_iri(graph_name: str) -> str:
    slug = graph_name.strip().replace(" ", "-")
    return f"{GRAPH_IRI_PREFIX}{slug}"


def iri_to_graph_name(graph_iri: str) -> str:
    if graph_iri.startswith(GRAPH_IRI_PREFIX):
        return graph_iri.removeprefix(GRAPH_IRI_PREFIX)
    return graph_iri
