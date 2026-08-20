import type { GraphSummary, IngestionRun, ValidationReport } from "./api";

export function summarizeObservability(
  runs: Pick<IngestionRun, "status">[],
  reports: Pick<ValidationReport, "conforms">[],
  graphs: GraphSummary[],
) {
  const completedRuns = runs.filter((run) => run.status === "completed").length;
  const conformingReports = reports.filter((report) => report.conforms).length;

  return {
    graphCount: graphs.length,
    runCount: runs.length,
    failedRuns: runs.length - completedRuns,
    workflowSuccessRate: runs.length ? Math.round((completedRuns / runs.length) * 100) : 0,
    validationSuccessRate: reports.length
      ? Math.round((conformingReports / reports.length) * 100)
      : 0,
  };
}
