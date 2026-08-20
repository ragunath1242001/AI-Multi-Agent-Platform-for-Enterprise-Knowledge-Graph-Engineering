import {
  executeSparqlQuery,
  listGraphs,
  listIngestionRuns,
  listOntologyModules,
  listValidationReports,
  startIngestionRun,
} from "./api";

export type DemoStepId = "ontology" | "agents" | "validation" | "graph" | "query" | "observability";
export type DemoStepStatus = "pending" | "running" | "completed" | "failed";

export const DEMO_STEPS: { id: DemoStepId; label: string }[] = [
  { id: "ontology", label: "Load ontology modules" },
  { id: "agents", label: "Run multi-agent ingestion" },
  { id: "validation", label: "Verify SHACL validation" },
  { id: "graph", label: "Confirm graph promotion" },
  { id: "query", label: "Execute SPARQL query" },
  { id: "observability", label: "Refresh observability" },
];

type Progress = (id: DemoStepId, status: DemoStepStatus, detail: string) => void;

export async function runProjectDemo(progress: Progress) {
  async function step<T>(id: DemoStepId, action: () => Promise<[T, string]>) {
    progress(id, "running", "In progress");
    try {
      const [value, detail] = await action();
      progress(id, "completed", detail);
      return value;
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Demo step failed.";
      progress(id, "failed", detail);
      throw error;
    }
  }

  const modules = await step("ontology", async () => {
    const items = await listOntologyModules();
    return [items, `${items.length} ontology modules loaded.`];
  });
  const run = await step("agents", async () => {
    const item = await startIngestionRun("synthetic-medical-cohort");
    if (item.status !== "completed") throw new Error(item.error || "Agent workflow did not complete.");
    return [item, `${item.steps.length} steps completed; ${item.triple_count ?? 0} triples promoted.`];
  });
  const reports = await step("validation", async () => {
    const items = await listValidationReports();
    const report = items.find((item) => item.id === run.validation_report_id) ?? items[0];
    if (!report?.conforms) throw new Error("The latest validation report has violations.");
    return [items, `${items.length} reports available; latest graph conforms.`];
  });
  const graphs = await step("graph", async () => {
    const items = await listGraphs();
    if (!items.some((item) => item.graph_name === run.graph_name)) {
      throw new Error("Promoted graph is missing from the inventory.");
    }
    return [items, `${items.length} named graphs available.`];
  });
  const query = await step("query", async () => {
    const result = await executeSparqlQuery(
      "SELECT ?graph (COUNT(?subject) AS ?triples) WHERE { GRAPH ?graph { ?subject ?predicate ?object } } GROUP BY ?graph ORDER BY DESC(?triples)",
    );
    const count = result.results.results?.bindings?.length ?? 0;
    return [result, `${count} graph rows returned.`];
  });
  const runs = await step("observability", async () => {
    const items = await listIngestionRuns();
    return [items, `${items.length} workflow runs recorded.`];
  });

  return {
    ontologyModules: modules.length,
    workflowRuns: runs.length,
    validationReports: reports.length,
    namedGraphs: graphs.length,
    queryRows: query.results.results?.bindings?.length ?? 0,
  };
}
