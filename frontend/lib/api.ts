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

export type NaturalLanguageQueryResult = {
  query: string;
  explanation: string;
};

export type IngestionDataset = {
  key: string;
  graph_name: string;
  title: string;
  path: string;
};

export type IngestionRun = {
  id: string;
  dataset_key: string;
  graph_name: string;
  status: string;
  steps: { name: string; status: string; detail: string }[];
  validation_report_id?: string | null;
  ontology_versions: OntologyVersion[];
  triple_count: number | null;
  error: string | null;
  created_at: string;
  updated_at: string;
};

export type OntologyModule = {
  key: string;
  title: string;
  path: string;
  namespace: string;
  version: string | null;
  triple_count: number;
  class_count: number;
  object_property_count: number;
  datatype_property_count: number;
  turtle: string;
};

export type OntologyVersion = {
  id: string;
  ontology_key: string;
  title: string;
  path: string;
  namespace: string;
  version: string | null;
  checksum: string;
  graph_iri: string;
  triple_count: number;
  created_at: string;
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

export async function translateNaturalLanguageQuery(
  question: string,
): Promise<NaturalLanguageQueryResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graphs/translate-query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail || "Query translation failed.");
  }

  return response.json();
}

export async function listIngestionDatasets(): Promise<IngestionDataset[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/workflows/ingestion/datasets`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Could not load ingestion datasets.");
  }

  return response.json();
}

export async function listIngestionRuns(): Promise<IngestionRun[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/workflows/ingestion/runs`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Could not load agent runs.");
  }

  return response.json();
}

export async function startIngestionRun(datasetKey: string): Promise<IngestionRun> {
  const response = await fetch(`${API_BASE_URL}/api/v1/workflows/ingestion/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_key: datasetKey }),
  });

  if (!response.ok) {
    throw new Error("Agent workflow failed.");
  }

  return response.json();
}

export async function listOntologyModules(): Promise<OntologyModule[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graphs/ontology/modules`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Could not load ontology modules.");
  }

  return response.json();
}

export async function listOntologyVersions(): Promise<OntologyVersion[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graphs/ontology/versions`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Could not load ontology version history.");
  }

  return response.json();
}
