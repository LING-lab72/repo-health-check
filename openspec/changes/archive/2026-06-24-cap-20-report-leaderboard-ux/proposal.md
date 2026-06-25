# cap-20 Report, Leaderboard, and UX Optimization

## Summary

Improve high-friction product flows after the security/architecture hardening pass:

- Make report loading cache-aware instead of forcing a synchronous re-analysis.
- Show staged analysis progress while background analysis is running.
- Auto-request AI diagnosis during the primary analysis flow.
- Add a one-click path from a report to repository comparison.
- Add backend and frontend leaderboard pagination.
- Upgrade HTML export from a basic table to a visual report with an inline radar chart.
- Show a trend/reference chart even when only one history point exists.
- Add a live badge color preview in the report page.

## Motivation

The previous implementation could re-clone and re-analyze on every report page refresh, making cache ineffective and turning a normal refresh into a multi-minute wait. Leaderboard data was returned as a full list, which would become slow as the dataset grew. Exported reports were technically useful but visually weak.

## Scope

In scope:

- Frontend report loading, polling, progress UI, badge preview, compare shortcut, and AI diagnosis flow.
- Backend leaderboard pagination with compatibility for the existing unpaginated endpoint behavior.
- Exported HTML report layout and radar SVG generation.
- OpenSpec and tests for the new behavior.

Out of scope:

- PDF export and social share image generation. These require new browser-side rendering dependencies and should be handled as a separate change.
- Exact backend progress telemetry. Current UI uses deterministic staged progress while polling the existing status endpoint.
