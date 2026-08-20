import { describe, expect, it } from "vitest";

import { summarizeObservability } from "./observability";

describe("observability summary", () => {
  it("calculates workflow and validation health", () => {
    const summary = summarizeObservability(
      [{ status: "completed" }, { status: "failed" }],
      [{ conforms: true }, { conforms: true }, { conforms: false }],
      [
        { graph_name: "one", graph_iri: "https://example.com/one" },
        { graph_name: "two", graph_iri: "https://example.com/two" },
      ],
    );

    expect(summary).toEqual({
      graphCount: 2,
      runCount: 2,
      failedRuns: 1,
      workflowSuccessRate: 50,
      validationSuccessRate: 67,
    });
  });
});
