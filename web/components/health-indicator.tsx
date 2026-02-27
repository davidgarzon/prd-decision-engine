"use client";

import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api";
import { cn } from "@/lib/utils";

export function HealthIndicator() {
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    async function poll() {
      const ok = await checkHealth();
      if (mounted) setHealthy(ok);
    }
    poll();
    const id = setInterval(poll, 15_000);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, []);

  const label =
    healthy === null
      ? "Checking…"
      : healthy
        ? "Connected"
        : "Disconnected";

  const dotColor =
    healthy === null
      ? "bg-muted-foreground"
      : healthy
        ? "bg-emerald-500"
        : "bg-red-500";

  return (
    <div
      className={cn(
        "flex items-center gap-2 text-xs font-medium",
        healthy === null
          ? "text-muted-foreground"
          : healthy
            ? "text-emerald-600"
            : "text-red-500",
      )}
    >
      <span className="relative flex h-2 w-2">
        {healthy !== false && (
          <span
            className={cn(
              "absolute inline-flex h-full w-full animate-ping rounded-full opacity-75",
              dotColor,
            )}
          />
        )}
        <span
          className={cn(
            "relative inline-flex h-2 w-2 rounded-full",
            dotColor,
          )}
        />
      </span>
      {label}
    </div>
  );
}
