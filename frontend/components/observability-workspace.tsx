"use client";

import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

import { MetricCard } from "@/components/metric-card";
import {
  listGraphs,
  listIngestionRuns,
  listValidationReports,
  type GraphSummary,
  type IngestionRun,
  type ValidationReport,
} from "@/lib/api";
import { summarizeObservability } from "@/lib/observability";

export function ObservabilityWorkspace() {
  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [reports, setReports] = useState<ValidationReport[]>([]);
  const [graphs, setGraphs] = useState<GraphSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [recentRuns, recentReports, namedGraphs] = await Promise.all([
        listIngestionRuns(),
        listValidationReports(),
        listGraphs(),
      ]);
      setRuns(recentRuns);
      setReports(recentReports);
      setGraphs(namedGraphs);
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load observability data.");
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  const summary = summarizeObservability(runs, reports, graphs);

  return (
    <>
      <section className="metrics" aria-label="Operational health">
        <MetricCard label="Named graphs" value={String(summary.graphCount)} detail="Queryable graph inventory" />
        <MetricCard label="Workflow success" value={`${summary.workflowSuccessRate}%`} detail={`${summary.runCount} recorded runs`} />
        <MetricCard label="Validation success" value={`${summary.validationSuccessRate}%`} detail={`${reports.length} validation reports`} />
        <MetricCard label="Failed workflows" value={String(summary.failedRuns)} detail="Runs requiring attention" />
      </section>

      {error ? <p className="error-text">{error}</p> : null}

      <section className="panel-grid observability-grid">
        <div className="panel">
          <div className="panel-heading">
            <div>
              <h2>Agent runs</h2>
              <span>Latest orchestration outcomes</span>
            </div>
            <button type="button" className="icon-action" onClick={() => void refresh()}>
              <RefreshCw size={16} aria-hidden="true" />
              Refresh
            </button>
          </div>
          <div className="activity-list">
            {runs.length ? runs.slice(0, 10).map((run) => (
              <article key={run.id}>
                <div>
                  <strong>{run.graph_name}</strong>
                  <span>{new Date(run.updated_at).toLocaleString()}</span>
                </div>
                <span className={`status-badge ${run.status}`}>{run.status}</span>
              </article>
            )) : <p className="empty-text">No workflow runs recorded.</p>}
          </div>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <div>
              <h2>Validation activity</h2>
              <span>Latest SHACL outcomes</span>
            </div>
          </div>
          <div className="activity-list">
            {reports.length ? reports.slice(0, 10).map((report) => (
              <article key={report.id}>
                <div>
                  <strong>{report.graph_name}</strong>
                  <span>{new Date(report.created_at).toLocaleString()}</span>
                </div>
                <span className={`status-badge ${report.conforms ? "completed" : "failed"}`}>
                  {report.conforms ? "conforms" : "violations"}
                </span>
              </article>
            )) : <p className="empty-text">No validation reports recorded.</p>}
          </div>
        </div>
      </section>
    </>
  );
}
