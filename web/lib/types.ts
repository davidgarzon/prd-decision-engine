export interface Gap {
  area: string;
  why: string;
  suggested_fix: string;
}

export interface Risk {
  risk: string;
  impact: string;
  mitigation: string;
}

export interface MetricDef {
  metric: string;
  definition: string;
}

export interface Experiment {
  hypothesis: string;
  metric: string;
  design: string;
}

export interface ScoringRubricItem {
  criterion: string;
  weight: number;
  score: number;
  notes: string;
}

export type RiskLevel = "low" | "medium" | "high";

export interface ImpactProfile {
  delivery_risk: RiskLevel;
  strategic_alignment: RiskLevel;
  measurement_maturity: RiskLevel;
}

export type ReadinessLevel =
  | "Draft"
  | "Pre-Discovery"
  | "Validation Ready"
  | "Build Ready"
  | "Board Ready";

export interface DecisionTrace {
  scoring_rubric: ScoringRubricItem[];
  assumptions: string[];
  confidence: number;
  impact_profile?: ImpactProfile;
  readiness_level?: ReadinessLevel;
}

export interface ReviewResponse {
  overall_score: number;
  summary: string;
  strengths: string[];
  gaps: Gap[];
  risks: Risk[];
  questions: string[];
  metrics: MetricDef[];
  suggested_experiments: Experiment[];
  decision_trace: DecisionTrace;
}

export interface ReviewRequest {
  prd_markdown: string;
  product_context?: Record<string, unknown>;
  audience?: string;
  mode?: "auto" | "mock";
}
