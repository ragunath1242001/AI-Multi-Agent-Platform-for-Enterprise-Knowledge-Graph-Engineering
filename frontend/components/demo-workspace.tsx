"use client";

import { CheckCircle2, Loader2, Play, XCircle } from "lucide-react";
import { useState } from "react";

import {
  DEMO_STEPS,
  runProjectDemo,
  type DemoStepId,
  type DemoStepStatus,
} from "@/lib/demo";

type Step = { id: DemoStepId; label: string; status: DemoStepStatus; detail: string };

function freshSteps(): Step[] {
  return DEMO_STEPS.map((step) => ({ ...step, status: "pending", detail: "Waiting" }));
}

export function DemoWorkspace() {
  const [steps, setSteps] = useState(freshSteps);
  const [summary, setSummary] = useState<Record<string, number> | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runDemo() {
    setSteps(freshSteps());
    setSummary(null);
    setError(null);
    setIsRunning(true);

    try {
      const result = await runProjectDemo((id, status, detail) => {
        setSteps((current) => current.map((step) => step.id === id ? { ...step, status, detail } : step));
      });
      setSummary(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Project demo failed.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <section className="panel demo-panel">
      <div className="panel-heading">
        <div>
          <h2>End-to-end platform demo</h2>
          <span>Ontology → agents → validation → graph store → query → observability</span>
        </div>
        <button type="button" className="primary-action" disabled={isRunning} onClick={() => void runDemo()}>
          {isRunning ? <Loader2 size={18} aria-hidden="true" /> : <Play size={18} aria-hidden="true" />}
          {isRunning ? "Running demo" : "Run full demo"}
        </button>
      </div>

      <div className="demo-steps">
        {steps.map((step, index) => (
          <article key={step.id} className={step.status}>
            <span className="demo-step-number">{index + 1}</span>
            <div>
              <strong>{step.label}</strong>
              <p>{step.detail}</p>
            </div>
            {step.status === "running" ? <Loader2 aria-label="Running" /> : null}
            {step.status === "completed" ? <CheckCircle2 aria-label="Completed" /> : null}
            {step.status === "failed" ? <XCircle aria-label="Failed" /> : null}
          </article>
        ))}
      </div>

      {summary ? <pre className="demo-summary">{JSON.stringify(summary, null, 2)}</pre> : null}
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
