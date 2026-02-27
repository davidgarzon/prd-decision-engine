"use client";

import { useState } from "react";
import {
  Menu,
  FileText,
  Braces,
  BookOpen,
  ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { HealthIndicator } from "@/components/health-indicator";
import { API_BASE } from "@/lib/api";

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="flex h-full flex-col">
      {/* Brand */}
      <div className="flex h-14 items-center gap-2.5 px-5">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-xs font-bold text-primary-foreground">
          P
        </div>
        <span className="font-semibold tracking-tight">PRD Engine</span>
      </div>

      <Separator />

      <nav className="flex-1 space-y-1 px-3 py-4">
        <p className="mb-2 px-2 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
          Menu
        </p>
        <a
          href="/"
          onClick={onNavigate}
          className="flex items-center gap-3 rounded-md bg-accent px-3 py-2 text-sm font-medium text-accent-foreground"
        >
          <FileText className="h-4 w-4" />
          Review
        </a>
      </nav>

      <Separator />

      <div className="space-y-1 px-3 py-4">
        <p className="mb-2 px-2 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
          Resources
        </p>
        <a
          href={`${API_BASE}/docs`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <BookOpen className="h-4 w-4" />
          API Docs
          <ExternalLink className="ml-auto h-3 w-3 opacity-50" />
        </a>
        <a
          href={`${API_BASE}/schema`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <Braces className="h-4 w-4" />
          Schema
          <ExternalLink className="ml-auto h-3 w-3 opacity-50" />
        </a>
      </div>

      <div className="mt-auto px-5 py-4">
        <p className="text-[11px] text-muted-foreground/60">v0.1.0</p>
      </div>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Desktop sidebar */}
      <aside className="hidden w-60 shrink-0 border-r bg-muted/40 lg:block">
        <SidebarContent />
      </aside>

      {/* Mobile sidebar */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent side="left" className="w-60 p-0">
          <SidebarContent onNavigate={() => setOpen(false)} />
        </SheetContent>
      </Sheet>

      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-14 shrink-0 items-center gap-4 border-b px-4 lg:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="shrink-0 lg:hidden"
            onClick={() => setOpen(true)}
          >
            <Menu className="h-5 w-5" />
            <span className="sr-only">Menu</span>
          </Button>
          <h2 className="text-sm font-semibold">Review</h2>
          <div className="flex-1" />
          <HealthIndicator />
        </header>

        <main className="flex-1 overflow-hidden">{children}</main>
      </div>
    </div>
  );
}
