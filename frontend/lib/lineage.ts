import type { GraphLineage } from "./api";

export type LineageStage = {
  id: string;
  label: string;
  summary: string;
  details: { label: string; value: string }[];
};

export function buildLineageStages(lineage: GraphLineage): LineageStage[] {
  return [
    {
      id: "source",
      label: "Source",
      summary: lineage.source_uri.split("/").pop() ?? lineage.source_uri,
      details: [
        { label: "Path", value: lineage.source_uri },
        { label: "SHA-256", value: lineage.source_checksum },
      ],
    },
    {
      id: "workflow",
      label: "Workflow",
      summary: lineage.workflow_run_id.slice(0, 8),
      details: [
        { label: "Run ID", value: lineage.workflow_run_id },
        { label: "Dataset", value: lineage.dataset_key },
      ],
    },
    {
      id: "validation",
      label: "Validation",
      summary: "Conformed",
      details: [
        { label: "Report ID", value: lineage.validation_report_id },
        { label: "Result", value: "SHACL validation passed" },
      ],
    },
    {
      id: "ontologies",
      label: "Ontologies",
      summary: `${lineage.ontology_versions.length} snapshots`,
      details: [
        {
          label: "Versions",
          value: lineage.ontology_versions
            .map(
              (version) =>
                `${version.ontology_key}@${version.version ?? version.checksum.slice(0, 12)}`,
            )
            .join(", "),
        },
      ],
    },
    {
      id: "graph",
      label: "Fuseki graph",
      summary: `${lineage.triple_count} triples`,
      details: [
        { label: "Named graph", value: lineage.graph_iri },
        { label: "Triple count", value: String(lineage.triple_count) },
        { label: "Promoted", value: new Date(lineage.promoted_at).toLocaleString() },
      ],
    },
  ];
}
