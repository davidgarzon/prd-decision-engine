"use client";

import { useState, type ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

interface Props {
  title: string;
  count?: number;
  defaultOpen?: boolean;
  children: ReactNode;
}

export function ReviewSection({
  title,
  count,
  defaultOpen = false,
  children,
}: Props) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <div className="rounded-lg border bg-card">
        <CollapsibleTrigger className="flex w-full items-center justify-between px-4 py-3 text-left transition-colors hover:bg-accent/50">
          <span className="text-sm font-semibold">
            {title}
            {count != null && (
              <span className="ml-1.5 text-xs font-normal text-muted-foreground">
                ({count})
              </span>
            )}
          </span>
          <ChevronDown
            className={cn(
              "h-4 w-4 text-muted-foreground transition-transform duration-200",
              open && "rotate-180",
            )}
          />
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="border-t px-4 py-3">{children}</div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}
