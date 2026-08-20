import { Activity, Bot, BrainCircuit, Database, GitBranch, Search, ShieldCheck } from "lucide-react";

import { AgentsWorkspace } from "@/components/agents-workspace";
import { PipelineStep } from "@/components/pipeline-step";

const agents = [
  { title: "Ontology Agent", status: "Workflow node", icon: GitBranch },
  { title: "RDF Generation Agent", status: "Workflow node", icon: Bot },
  { title: "Validation Agent", status: "Workflow node", icon: ShieldCheck },
  { title: "Reasoning Agent", status: "Workflow node", icon: BrainCircuit },
  { title: "Query Agent", status: "Defined", icon: Search },
  { title: "Observability Agent", status: "Defined", icon: Activity },
];

export default function AgentsPage() {
  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <Database aria-hidden="true" />
          <span>SemanticOps</span>
        </div>
        <nav>
          <a href="/">Operations</a>
          <a className="active" href="/agents">Agents</a>
          <a href="/ontology">Ontology</a>
          <a href="/validation">Validation</a>
          <a href="/observability">Observability</a>
          <a href="/demo">Demo</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">LangGraph orchestration</p>
            <h1>Agents</h1>
          </div>
        </header>

        <section className="panel agent-registry">
          <div className="panel-heading">
            <h2>Agent registry</h2>
            <span>Explicit roles and responsibility boundaries</span>
          </div>
          <div className="agent-grid">
            {agents.map((agent) => <PipelineStep key={agent.title} {...agent} />)}
          </div>
        </section>

        <AgentsWorkspace />
      </section>
    </main>
  );
}
