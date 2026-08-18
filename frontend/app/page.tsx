import { Activity, Bot, Database, GitBranch, Search, ShieldCheck } from "lucide-react";
import { MetricCard } from "@/components/metric-card";
import { PipelineStep } from "@/components/pipeline-step";
import { ValidationWorkspace } from "@/components/validation-workspace";

const pipeline = [
  { title: "Ontology Design", status: "Ready", icon: GitBranch },
  { title: "RDF Generation", status: "Queued", icon: Bot },
  { title: "SHACL Validation", status: "Idle", icon: ShieldCheck },
  { title: "Reasoning", status: "Idle", icon: Activity },
];

export default function Home() {
  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <Database aria-hidden="true" />
          <span>SemanticOps</span>
        </div>
        <nav>
          <a className="active" href="#">Operations</a>
          <a href="#">Agents</a>
          <a href="#">Ontology</a>
          <a href="#">Validation</a>
          <a href="#">Observability</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Knowledge graph engineering</p>
            <h1>Enterprise Semantic Operations</h1>
          </div>
          <button type="button" className="primary-action">
            <Search size={18} aria-hidden="true" />
            Query graph
          </button>
        </header>

        <section className="metrics" aria-label="Platform metrics">
          <MetricCard label="Named graphs" value="12" detail="3 pending validation" />
          <MetricCard label="SHACL conformance" value="98.4%" detail="Last run 14 min ago" />
          <MetricCard label="Agent runs" value="327" detail="24h orchestration volume" />
          <MetricCard label="Reasoning jobs" value="8" detail="2 scheduled" />
        </section>

        <section className="panel-grid">
          <div className="panel">
            <div className="panel-heading">
              <h2>Agent Pipeline</h2>
              <span>LangGraph orchestration</span>
            </div>
            <div className="pipeline">
              {pipeline.map((step) => (
                <PipelineStep key={step.title} {...step} />
              ))}
            </div>
          </div>

          <div className="panel query-panel">
            <div className="panel-heading">
              <h2>Natural Language Query</h2>
              <span>SPARQL translation workspace</span>
            </div>
            <label htmlFor="query">Question</label>
            <textarea
              id="query"
              defaultValue="Which policies describe customer account risk controls?"
            />
            <div className="result-preview">
              <code>SELECT ?policy ?control WHERE {"{ ... }"}</code>
            </div>
          </div>
        </section>

        <section className="panel validation-panel">
          <div className="panel-heading">
            <h2>SHACL Validation</h2>
            <span>Persisted report workflow</span>
          </div>
          <ValidationWorkspace />
        </section>
      </section>
    </main>
  );
}
