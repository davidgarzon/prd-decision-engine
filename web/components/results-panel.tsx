import type { ReviewResponse } from "@/lib/types";
import { Loader2, FileText, AlertCircle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { ScoreHeader } from "./score-header";
import { RubricTable } from "./rubric-table";
import { ReviewSection } from "./review-section";

interface Props {
  result: ReviewResponse | null;
  loading: boolean;
  error: { status: number; message: string } | null;
}

export function ResultsPanel({ result, loading, error }: Props) {
  if (loading) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 text-muted-foreground">
        <Loader2 className="h-8 w-8 animate-spin" />
        <p className="text-sm">Analyzing PRD&hellip;</p>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive/50 bg-destructive/5">
        <CardContent className="flex items-start gap-3 pt-6">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />
          <div>
            <p className="text-sm font-semibold text-destructive">
              Analysis Failed
            </p>
            {error.status > 0 && (
              <p className="mt-0.5 text-xs text-destructive/70">
                HTTP {error.status}
              </p>
            )}
            <p className="mt-2 whitespace-pre-wrap text-sm text-destructive/80">
              {error.message}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!result) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 text-muted-foreground">
        <FileText className="h-12 w-12 opacity-20" />
        <div className="text-center">
          <p className="text-sm font-medium">No analysis yet</p>
          <p className="mt-1 text-xs">
            Paste a PRD and click{" "}
            <strong className="text-foreground/70">Analyze</strong> to see
            results
          </p>
        </div>
      </div>
    );
  }

  const {
    summary,
    strengths,
    gaps,
    risks,
    questions,
    metrics,
    suggested_experiments,
    decision_trace,
  } = result;

  return (
    <div className="space-y-6">
      <ScoreHeader result={result} />

      <p className="text-sm leading-relaxed text-muted-foreground">{summary}</p>

      <div>
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          Scoring Rubric
        </h3>
        <RubricTable rubric={decision_trace.scoring_rubric} />
      </div>

      <div className="space-y-2">
        {strengths?.length > 0 && (
          <ReviewSection title="Strengths" count={strengths.length} defaultOpen>
            <ul className="list-disc space-y-1 pl-5 text-sm text-foreground/80">
              {strengths.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </ReviewSection>
        )}

        {gaps?.length > 0 && (
          <ReviewSection title="Gaps" count={gaps.length}>
            <div className="space-y-3">
              {gaps.map((g, i) => (
                <div key={i} className="text-sm">
                  <p className="font-medium">{g.area}</p>
                  <p className="text-muted-foreground">{g.why}</p>
                  <p className="mt-0.5 font-medium text-primary/80">
                    &rarr; {g.suggested_fix}
                  </p>
                </div>
              ))}
            </div>
          </ReviewSection>
        )}

        {risks?.length > 0 && (
          <ReviewSection title="Risks" count={risks.length}>
            <div className="space-y-3">
              {risks.map((r, i) => (
                <div key={i} className="text-sm">
                  <p className="font-medium">{r.risk}</p>
                  <p className="text-muted-foreground">Impact: {r.impact}</p>
                  <p className="mt-0.5 text-emerald-700">
                    Mitigation: {r.mitigation}
                  </p>
                </div>
              ))}
            </div>
          </ReviewSection>
        )}

        {questions?.length > 0 && (
          <ReviewSection title="Open Questions" count={questions.length}>
            <ul className="list-disc space-y-1 pl-5 text-sm text-foreground/80">
              {questions.map((q, i) => (
                <li key={i}>{q}</li>
              ))}
            </ul>
          </ReviewSection>
        )}

        {metrics?.length > 0 && (
          <ReviewSection title="Suggested Metrics" count={metrics.length}>
            <div className="space-y-2">
              {metrics.map((m, i) => (
                <div key={i} className="text-sm">
                  <p className="font-medium">{m.metric}</p>
                  <p className="text-muted-foreground">{m.definition}</p>
                </div>
              ))}
            </div>
          </ReviewSection>
        )}

        {suggested_experiments?.length > 0 && (
          <ReviewSection
            title="Experiments"
            count={suggested_experiments.length}
          >
            <div className="space-y-3">
              {suggested_experiments.map((e, i) => (
                <div key={i} className="text-sm">
                  <p className="font-medium">{e.hypothesis}</p>
                  <p className="text-muted-foreground">Metric: {e.metric}</p>
                  <p className="text-muted-foreground">Design: {e.design}</p>
                </div>
              ))}
            </div>
          </ReviewSection>
        )}

        {decision_trace.assumptions?.length > 0 && (
          <ReviewSection
            title="Assumptions"
            count={decision_trace.assumptions.length}
          >
            <ul className="list-disc space-y-1 pl-5 text-sm text-foreground/80">
              {decision_trace.assumptions.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </ReviewSection>
        )}
      </div>
    </div>
  );
}
