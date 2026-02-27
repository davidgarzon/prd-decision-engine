"use client";

import { useState, useCallback } from "react";
import {
  Loader2,
  Zap,
  RotateCcw,
  Copy,
  Check,
  Download,
} from "lucide-react";
import type { ReviewResponse } from "@/lib/types";
import { submitReview, ApiError } from "@/lib/api";
import { SAMPLE_PRD } from "@/lib/sample-prd";
import { Button } from "@/components/ui/button";
import { ResultsPanel } from "@/components/results-panel";
import { cn } from "@/lib/utils";

export default function Home() {
  const [prdText, setPrdText] = useState(SAMPLE_PRD);
  const [result, setResult] = useState<ReviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{
    status: number;
    message: string;
  } | null>(null);
  const [copied, setCopied] = useState(false);
  const [mobileView, setMobileView] = useState<"editor" | "results">(
    "editor",
  );

  const handleAnalyze = useCallback(async () => {
    if (!prdText.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await submitReview({ prd_markdown: prdText });
      setResult(data);
      setMobileView("results");
    } catch (err) {
      if (err instanceof ApiError) {
        setError({ status: err.status, message: err.message });
      } else {
        setError({
          status: 0,
          message: "Could not reach the API. Is the backend running?",
        });
      }
      setMobileView("results");
    } finally {
      setLoading(false);
    }
  }, [prdText]);

  const handleCopy = useCallback(async () => {
    if (!result) return;
    await navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [result]);

  const handleDownload = useCallback(() => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "prd-review.json";
    a.click();
    URL.revokeObjectURL(url);
  }, [result]);

  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Mobile view toggle */}
      <div className="flex gap-1 border-b bg-muted/30 p-2 lg:hidden">
        <Button
          variant={mobileView === "editor" ? "secondary" : "ghost"}
          size="sm"
          className="flex-1"
          onClick={() => setMobileView("editor")}
        >
          Editor
        </Button>
        <Button
          variant={mobileView === "results" ? "secondary" : "ghost"}
          size="sm"
          className="flex-1"
          onClick={() => setMobileView("results")}
        >
          Results
          {result && (
            <span className="ml-1.5 rounded-sm bg-primary/10 px-1.5 text-[11px] tabular-nums">
              {result.overall_score}
            </span>
          )}
        </Button>
      </div>

      {/* Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* ── Editor panel ── */}
        <div
          className={cn(
            "flex flex-col",
            mobileView === "editor" ? "flex-1" : "hidden",
            "lg:flex lg:w-1/2 lg:border-r",
          )}
        >
          <div className="flex items-center justify-between px-4 py-3 lg:px-6">
            <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              PRD Markdown
            </h3>
            <span className="text-[11px] tabular-nums text-muted-foreground">
              {prdText.length.toLocaleString()} chars
            </span>
          </div>

          <div className="flex-1 px-4 pb-3 lg:px-6">
            <textarea
              className="h-full w-full resize-none rounded-lg border bg-background p-4 font-mono text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/30"
              value={prdText}
              onChange={(e) => setPrdText(e.target.value)}
              placeholder="Paste your PRD markdown here…"
              spellCheck={false}
            />
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap items-center gap-2 border-t px-4 py-3 lg:px-6">
            <Button
              onClick={handleAnalyze}
              disabled={loading || !prdText.trim()}
              size="sm"
            >
              {loading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Zap className="mr-2 h-4 w-4" />
              )}
              {loading ? "Analyzing…" : "Analyze PRD"}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPrdText(SAMPLE_PRD)}
            >
              <RotateCcw className="mr-2 h-3.5 w-3.5" />
              Sample
            </Button>

            <div className="flex-1" />

            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              disabled={!result}
            >
              {copied ? (
                <Check className="mr-1.5 h-3.5 w-3.5" />
              ) : (
                <Copy className="mr-1.5 h-3.5 w-3.5" />
              )}
              {copied ? "Copied" : "Copy"}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDownload}
              disabled={!result}
            >
              <Download className="mr-1.5 h-3.5 w-3.5" />
              JSON
            </Button>
          </div>
        </div>

        {/* ── Results panel ── */}
        <div
          className={cn(
            "flex-1 overflow-y-auto",
            mobileView === "results" ? "flex flex-col" : "hidden",
            "lg:flex lg:flex-col",
          )}
        >
          <div className="p-4 lg:p-6">
            <ResultsPanel result={result} loading={loading} error={error} />
          </div>
        </div>
      </div>
    </div>
  );
}
