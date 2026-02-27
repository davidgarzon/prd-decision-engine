export const SAMPLE_PRD = `# Feature: Smart Notifications

## Problem Statement

Users miss important updates because the current notification system sends too
many low-priority alerts. Support tickets mentioning "notification fatigue"
increased 34% last quarter.

## User Segments

- **Power users** (daily active, 15% of base) — need real-time, high-signal alerts
- **Casual users** (weekly active, 60% of base) — prefer digest-style summaries

## Scope

### MVP (Phase 1 — 6 weeks)
- ML-based notification priority scoring
- User preference center with category controls
- Quiet hours support

### Out of Scope
- Cross-platform push sync
- Third-party webhook integrations

## Success Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| Notification open rate | 12% | 25% |
| User-reported fatigue (survey) | 45% | < 20% |
| DAU retention (D14) | 62% | 68% |

## Risks & Dependencies

1. **ML model cold-start** — new users have no engagement history; mitigation: rule-based fallback for first 7 days.
2. **Notification service v2 dependency** — API not yet in staging; mitigation: feature flag to gate rollout.
3. **Compliance** — GDPR consent flow must cover preference data; mitigation: legal review in week 2.

## Solution Design

Priority scoring engine that consumes engagement signals (click, dismiss, snooze)
and outputs a 0–1 relevance score per notification. Exposed via internal REST API;
consumed by the delivery service.

## Rollout & Experimentation

- **Week 1–2:** Internal dogfood (5% of users, employees only)
- **Week 3–4:** A/B experiment — 20% cohort, measure open-rate lift
- **Week 5:** Decision gate — ship if open rate ≥ 20% and fatigue ≤ 25%
- **Week 6:** GA rollout with feature flag for instant kill-switch`;
