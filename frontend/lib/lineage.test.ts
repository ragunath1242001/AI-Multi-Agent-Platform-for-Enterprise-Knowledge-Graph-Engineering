import { describe, expect, it } from "vitest";

import type { GraphLineage } from "./api";
import { buildLineageStages } from "./lineage";

describe("lineage graph", () => {
  it("maps a promotion into five selectable stages", () => {
    const lineage: GraphLineage = {
      workflow_run_id: "run-12345678",
      dataset_key: "medical-cohort",
      graph_name: "medical-cohort",
      source_uri: "examples/medical-cohort.ttl",
      source_checksum: "a".repeat(64),
      validation_report_id: "report-12345678",
      ontology_versions: [
        {
          id: "ontology-1",
          ontology_key: "medical",
          title: "Medical",
          path: "ontologies/medical.ttl",
          namespace: "https://example.com/medical#",
          version: "1.0.0",
          checksum: "b".repeat(64),
          graph_iri: "https://example.com/graphs/medical",
          triple_count: 10,
          created_at: "2026-08-21T12:00:00Z",
        },
      ],
      graph_iri: "https://example.com/graphs/medical-cohort",
      triple_count: 115,
      promoted_at: "2026-08-21T12:00:00Z",
    };

    const stages = buildLineageStages(lineage);

    expect(stages.map((stage) => stage.label)).toEqual([
      "Source",
      "Workflow",
      "Validation",
      "Ontologies",
      "Fuseki graph",
    ]);
    expect(stages[3].details[0].value).toContain("medical@1.0.0");
    expect(stages[4].summary).toBe("115 triples");
  });
});
