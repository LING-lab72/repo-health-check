# Design

## Report Loading

`ReportPage` calls `POST /api/analyze` with `force_sync:false` and `skip_ai:false`.

- If the backend returns `code=0`, the page renders the cached or completed result immediately.
- If the backend returns `code=1`, the page polls `GET /api/analyze/status` with both `task_id` and `repo_url` until completion, failure, or timeout.
- A staged progress UI maps elapsed polling attempts to user-facing phases: cache check, clone, analysis, AI diagnosis, and report generation.

This uses the existing 30-minute in-memory cache TTL. Refreshes within TTL therefore return immediately without re-cloning.

## Leaderboard Pagination

`GET /api/leaderboard` remains backward compatible:

- Without `page`, it returns the legacy list.
- With `page` and `page_size`, it returns `{items,total,page,page_size,has_next}`.

SQLite window functions select the latest row per repository and compute previous-score trend data without loading the full history into Python.

## Exported Report

The export route renders a self-contained HTML document:

- Hero section with repo URL, score, and badge.
- Inline SVG radar chart generated server-side from dimension scores.
- Dimension score table with bounded bars.
- Optional AI diagnosis section.

All dynamic values are escaped or clamped before insertion into HTML/SVG/style contexts.

## Tradeoffs

- Progress phases are currently approximate because the backend status endpoint only exposes pending/completed/failed. This improves perceived progress without expanding backend task state.
- PDF export is deferred because the current frontend dependency set does not include `html2canvas` or `jspdf`, and adding them should be a separate dependency review.
