from dataclasses import dataclass
from urllib.parse import quote

import httpx


@dataclass(frozen=True)
class FusekiClient:
    endpoint_url: str
    username: str | None = None
    password: str | None = None

    async def put_graph(self, graph_iri: str, data_graph_ttl: str) -> None:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.put(
                f"{self.endpoint_url}/data?graph={quote(graph_iri, safe='')}",
                content=data_graph_ttl,
                headers={"Content-Type": "text/turtle"},
                auth=self._auth,
            )
            response.raise_for_status()

    async def execute_sparql(self, query: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.endpoint_url}/sparql",
                data={"query": query},
                headers={"Accept": "application/sparql-results+json"},
            )
            response.raise_for_status()
            return response.json()

    async def list_graphs(self) -> dict:
        return await self.execute_sparql(
            "SELECT DISTINCT ?graph WHERE { GRAPH ?graph { ?subject ?predicate ?object } } "
            "ORDER BY ?graph"
        )

    @property
    def _auth(self) -> tuple[str, str] | None:
        if self.username and self.password:
            return (self.username, self.password)
        return None
