"use client";

import { Loader2, Play, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

import {
  listIngestionDatasets,
  listIngestionRuns,
  startIngestionRun,
  type IngestionDataset,
  type IngestionRun,
} from "@/lib/api";

export function AgentsWorkspace() {
  const [datasets, setDatasets] = useState<IngestionDataset[]>([]);
  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [selected, setSelected] = useState("");
  const [activeRun, setActiveRun] = useState<IngestionRun | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [availableDatasets, recentRuns] = await Promise.all([
        listIngestionDatasets(),
        listIngestionRuns(),
      ]);
      setDatasets(availableDatasets);
      setRuns(recentRuns);
      setSelected((current) => current || availableDatasets[0]?.key || "");
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load agent workflows.");
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function runWorkflow() {
    if (!selected) return;
    setIsRunning(true);
    setError(null);

    try {
      const run = await startIngestionRun(selected);
      setActiveRun(run);
      setRuns((current) => [run, ...current.filter((item) => item.id !== run.id)]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Agent workflow failed.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <section className="panel agent-workspace">
      <div className="panel-heading">
        <div>
          <h2>Ingestion workflow</h2>
          <span>Load, validate, promote, and prepare a named graph</span>
        </div>
        <button type="button" className="icon-action" onClick={() => void refresh()}>
          <RefreshCw size={16} aria-hidden="true" />
          Refresh
        </button>
      </div>

      <div className="agent-runner">
        <div className="dataset-list">
          <label htmlFor="dataset">Knowledge asset</label>
          <select id="dataset" value={selected} onChange={(event) => setSelected(event.target.value)}>
            {datasets.map((dataset) => (
              <option key={dataset.key} value={dataset.key}>
                {dataset.title}
              </option>
            ))}
          </select>
          <button
            type="button"
            className="primary-action"
            disabled={!selected || isRunning}
            onClick={() => void runWorkflow()}
          >
            {isRunning ? <Loader2 size={18} aria-hidden="true" /> : <Play size={18} aria-hidden="true" />}
            Run agents
          </button>
          {error ? <p className="error-text">{error}</p> : null}
        </div>

        <div className="run-details">
          <h3>{activeRun ? activeRun.graph_name : "Latest run"}</h3>
          {activeRun ? (
            <ol>
              {activeRun.steps.map((step) => (
                <li key={step.name}>
                  <strong>{step.name}</strong>
                  <span>{step.status}</span>
                  <p>{step.detail}</p>
                </li>
              ))}
            </ol>
          ) : (
            <p className="empty-text">Choose a dataset and run the agent workflow.</p>
          )}
        </div>
      </div>

      <div className="recent-runs">
        <div className="section-heading">
          <h3>Recent runs</h3>
          <span>{runs.length} recorded</span>
        </div>
        <div className="report-list">
          {runs.length ? runs.slice(0, 8).map((run) => (
            <button key={run.id} type="button" onClick={() => setActiveRun(run)}>
              <span>{run.graph_name}</span>
              <strong>{run.status}</strong>
            </button>
          )) : <p className="empty-text">No agent runs yet.</p>}
        </div>
      </div>
    </section>
  );
}
