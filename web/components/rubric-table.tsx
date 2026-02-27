import type { ScoringRubricItem } from "@/lib/types";
import { cn } from "@/lib/utils";

function barColor(ratio: number): string {
  if (ratio >= 0.8) return "bg-emerald-500";
  if (ratio >= 0.6) return "bg-blue-500";
  if (ratio >= 0.4) return "bg-amber-500";
  return "bg-red-500";
}

interface Props {
  rubric: ScoringRubricItem[];
}

export function RubricTable({ rubric }: Props) {
  return (
    <div className="rounded-lg border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-muted/50 text-left text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
            <th className="px-4 py-2.5">Criterion</th>
            <th className="px-3 py-2.5 text-center">Wt</th>
            <th className="px-3 py-2.5 text-center">Score</th>
            <th className="hidden w-20 px-3 py-2.5 sm:table-cell" />
            <th className="hidden px-4 py-2.5 md:table-cell">Notes</th>
          </tr>
        </thead>
        <tbody>
          {rubric.map((item) => {
            const ratio = item.weight > 0 ? item.score / item.weight : 0;
            return (
              <tr
                key={item.criterion}
                className="border-b last:border-0 transition-colors hover:bg-muted/30"
              >
                <td className="px-4 py-3 font-medium whitespace-nowrap">
                  {item.criterion}
                </td>
                <td className="px-3 py-3 text-center text-muted-foreground tabular-nums">
                  {item.weight}
                </td>
                <td
                  className={cn(
                    "px-3 py-3 text-center font-semibold tabular-nums",
                    ratio >= 0.6
                      ? "text-foreground"
                      : "text-red-600",
                  )}
                >
                  {item.score}
                </td>
                <td className="hidden px-3 py-3 sm:table-cell">
                  <div className="h-1.5 w-full rounded-full bg-muted">
                    <div
                      className={cn(
                        "h-1.5 rounded-full transition-all",
                        barColor(ratio),
                      )}
                      style={{ width: `${ratio * 100}%` }}
                    />
                  </div>
                </td>
                <td className="hidden px-4 py-3 text-xs leading-relaxed text-muted-foreground md:table-cell">
                  {item.notes}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
