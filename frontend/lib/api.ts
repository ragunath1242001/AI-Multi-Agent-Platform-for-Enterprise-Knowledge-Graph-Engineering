const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type ValidationReport = {
  id: string;
  graph_name: string;
  conforms: boolean;
  report_text?: string;
  created_at: string;
};

export type ValidationRequest = {
  graph_name: string;
  data_graph_ttl: string;
  shacl_shapes_ttl: string;
};

export type GraphStoreResult = {
  graph_name: string;
  graph_iri: string;
  triple_count: number;
};

export type GraphSummary = {
  graph_name: string;
  graph_iri: string;
};

export type SparqlQueryResult = {
  results: {
    head?: { vars?: string[] };
    results?: {
      bindings?: Record<string, { type: string; value: string }>[];
    };
    [key: string]: unknown;
  };
};

export async function getHealth(): Promise<{ status: string; service: string }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
    next: { revalidate: 30 },
  });

  if (!response.ok) {
    throw new Error("SemanticOps API health check failed.");
  }

  return response.json();
}

export async function validateGraph(payload: ValidationRequest): Promise<ValidationReport> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graphs/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Graph validation failed.");
  }

  return response.json();
}

export async function listValidationReports(): Promise<ValidationReport[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graphs/validation-reports`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Could not load validation reports.");
  }

  return response.json();
}

export async function upsertGraph(payload: ValidationRequest): Promise<GraphStoreResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graphs/graphs`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      graph_name: payload.graph_name,
      data_graph_ttl: payload.data_graph_ttl,
    }),
  });

  if (!response.ok) {
    throw new Error("Could not promote graph to the graph store.");
  }

  return response.json();
}

export async function listGraphs(): Promise<GraphSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graphs/graphs`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Could not load graph inventory.");
  }

  return response.json();
}

export async function executeSparqlQuery(query: string): Promise<SparqlQueryResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graphs/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error("Graph query failed.");
  }

  return response.json();
}
