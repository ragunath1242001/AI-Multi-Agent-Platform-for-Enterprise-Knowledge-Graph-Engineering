import type { LucideIcon } from "lucide-react";

type PipelineStepProps = {
  title: string;
  status: string;
  icon: LucideIcon;
};

export function PipelineStep({ title, status, icon: Icon }: PipelineStepProps) {
  return (
    <article className="pipeline-step">
      <Icon size={20} aria-hidden="true" />
      <div>
        <h3>{title}</h3>
        <span>{status}</span>
      </div>
    </article>
  );
}

