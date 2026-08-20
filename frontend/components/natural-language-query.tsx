"use client";

import { Loader2, Play, Sparkles } from "lucide-react";
import { type FormEvent, useState } from "react";

import {
  executeSparqlQuery,
  translateNaturalLanguageQuery,
  type SparqlQueryResult,
} from "@/lib/api";

export function NaturalLanguageQuery() {
  const [question, setQuestion] = useState("Which policies describe customer account risk controls?");
  const [sparql, setSparql] = useState("");
  const [explanation, setExplanation] = useState("");
  const [result, setResult] = useState<SparqlQueryResult | null>(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function translate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsTranslating(true);
    setError(null);
    setResult(null);
    try {
      const translation = await translateNaturalLanguageQuery(question);
      setSparql(translation.query);
      setExplanation(translation.explanation);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Query translation failed.");
    } finally {
      setIsTranslating(false);
    }
  }

  async function runQuery() {
    setIsRunning(true);
    setError(null);
    try {
      setResult(await executeSparqlQuery(sparql));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Graph query failed.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div id="natural-language-query" className="panel query-panel">
      <div className="panel-heading">
        <h2>Natural Language Query</h2>
        <span>Inspect generated SPARQL before execution</span>
      </div>
      <form className="query-form" onSubmit={translate}>
        <label htmlFor="query-question">Question</label>
        <textarea id="query-question" value={question} onChange={(event) => setQuestion(event.target.value)} />
        <button type="submit" className="primary-action" disabled={isTranslating || !question.trim()}>
          {isTranslating ? <Loader2 size={18} aria-hidden="true" /> : <Sparkles size={18} aria-hidden="true" />}
          Translate to SPARQL
        </button>
      </form>

      <label htmlFor="generated-sparql">Generated SPARQL</label>
      <textarea
        id="generated-sparql"
        className="query-code"
        value={sparql}
        onChange={(event) => setSparql(event.target.value)}
        placeholder="Generated read-only SPARQL will appear here."
        spellCheck={false}
      />
      {explanation ? <p className="query-explanation">{explanation}</p> : null}
      <button type="button" className="secondary-action" disabled={!sparql || isRunning} onClick={() => void runQuery()}>
        {isRunning ? <Loader2 size={18} aria-hidden="true" /> : <Play size={18} aria-hidden="true" />}
        Run SPARQL
      </button>
      {result ? <pre className="query-results">{JSON.stringify(result.results, null, 2)}</pre> : null}
      {error ? <p className="error-text">{error}</p> : null}
    </div>
  );
}
