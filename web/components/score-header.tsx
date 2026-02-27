import type { ReviewResponse, RiskLevel, ReadinessLevel } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

function scoreColor(score: number): string {
  if (score >= 80) return "text-emerald-600";
  if (score >= 65) return "text-blue-600";
  if (score >= 45) return "text-amber-600";
  if (score >= 25) return "text-orange-600";
  return "text-red-600";
}

function readinessStyle(level: ReadinessLevel): string {
  const m: Record<ReadinessLevel, string> = {
    "Board Ready": "border-emerald-300 bg-emerald-50 text-emerald-700",
    "Build Ready": "border-blue-300 bg-blue-50 text-blue-700",
    "Validation Ready": "border-amber-300 bg-amber-50 text-amber-700",
    "Pre-Discovery": "border-orange-300 bg-orange-50 text-orange-700",
    Draft: "border-red-300 bg-red-50 text-red-700",
  };
  return m[level] ?? "";
}

function chipStyle(key: string, level: RiskLevel): string {
  const inverted = key === "delivery_risk";
  const isGood = inverted ? level === "low" : level === "high";
  const isBad = inverted ? level === "high" : level === "low";
  if (isGood) return "border-emerald-200 bg-emerald-50 text-emerald-700";
  if (isBad) return "border-red-200 bg-red-50 text-red-700";
  return "border-amber-200 bg-amber-50 text-amber-700";
}

const IMPACT_LABELS: Record<string, string> = {
  delivery_risk: "Delivery Risk",
  strategic_alignment: "Alignment",
  measurement_maturity: "Measurement",
};

interface Props {
  result: ReviewResponse;
}

export function ScoreHeader({ result }: Props) {
  const { overall_score, decision_trace } = result;
  const readiness = decision_trace.readiness_level;
  const confidence = decision_trace.confidence;
  const impact = decision_trace.impact_profile;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        <Card>
          <CardContent className="flex flex-col items-center justify-center p-4">
            <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
              Score
            </span>
            <span
              className={cn(
                "mt-1 text-4xl font-bold tabular-nums",
                scoreColor(overall_score),
              )}
            >
              {overall_score}
            </span>
            <span className="text-[11px] text-muted-foreground">/ 100</span>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex flex-col items-center justify-center p-4">
            <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
              Readiness
            </span>
            {readiness ? (
              <Badge
                variant="outline"
                className={cn("mt-2.5", readinessStyle(readiness))}
              >
                {readiness}
              </Badge>
            ) : (
              <span className="mt-2 text-sm text-muted-foreground">&mdash;</span>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex flex-col items-center justify-center p-4">
            <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
              Confidence
            </span>
            <span className="mt-1 text-4xl font-bold tabular-nums">
              {confidence}
            </span>
            <span className="text-[11px] text-muted-foreground">%</span>
          </CardContent>
        </Card>
      </div>

      {impact && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(impact).map(([key, level]) => (
            <Badge
              key={key}
              variant="outline"
              className={cn("text-[11px]", chipStyle(key, level))}
            >
              {IMPACT_LABELS[key] ?? key}:
              <span className="ml-1 font-bold capitalize">{level}</span>
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
