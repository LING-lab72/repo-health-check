## 1. Report Flow

- [x] 1.1 Change ReportPage from `force_sync:true` to async cache-aware analysis.
- [x] 1.2 Poll `/api/analyze/status` for pending background tasks.
- [x] 1.3 Add staged progress UI for cache, clone, analysis, AI diagnosis, and report generation.
- [x] 1.4 Send `skip_ai:false` in the primary report request so AI diagnosis is automatic.
- [x] 1.5 Add report-to-compare shortcut with the current repository prefilled.
- [x] 1.6 Add animated live badge color preview.

## 2. Leaderboard

- [x] 2.1 Add SQLite-backed paginated leaderboard retrieval.
- [x] 2.2 Keep legacy unpaginated `/api/leaderboard` behavior.
- [x] 2.3 Update LeaderboardPage to request paginated data and render controls.
- [x] 2.4 Add backend pagination regression test.

## 3. Export and Trend UX

- [x] 3.1 Upgrade exported HTML report layout.
- [x] 3.2 Add static inline SVG radar chart to exported reports.
- [x] 3.3 Add radar SVG escaping regression test.
- [x] 3.4 Show history chart for one or more records with an industry/reference line.

## 4. Verification

- [x] 4.1 Frontend lint passed.
- [x] 4.2 Frontend Vitest passed.
- [x] 4.3 Frontend production build passed.
- [x] 4.4 Backend syntax check passed.
- [x] 4.5 Targeted backend pytest passed for leaderboard/export/cache.
- [x] 4.6 Full backend pytest attempted; local command timed out after 184 seconds before returning detailed output.

## 5. No-Key AI Diagnosis Follow-up

- [x] 5.1 Confirm backend `ai_diagnose()` falls back to local rule diagnosis when no API key exists.
- [x] 5.2 Keep ReportPage primary request on `skip_ai=false` so diagnosis runs automatically without a second click.
- [x] 5.3 Make Compare API/UI request diagnosis by default; no-key mode uses local rules.
- [x] 5.4 Update frontend copy to explain that API Key is optional and only upgrades diagnosis quality.
- [x] 5.5 Add regression coverage for no-key local diagnosis with issue hints.

## 6. Export and Share Enhancements

- [x] 6.1 Add language distribution pie chart from `code_quality.details.language_breakdown`.
- [x] 6.2 Add browser PDF export flow based on the existing HTML report.
- [x] 6.3 Add canvas-based PNG share card generation.
- [x] 6.4 Add frontend tests for language extraction, color normalization, and empty chart state.
- [x] 6.5 Update `report-export` OpenSpec requirements.

## 7. PK Arena and Wrapped Poster

- [x] 7.1 Add ComparePage PK arena with animated health bars and winner display.
- [x] 7.2 Add downloadable PNG PK poster generation.
- [x] 7.3 Upgrade report share card to Wrapped-style messaging with peer percentile and dominant language.
- [x] 7.4 Add regression coverage for peer percentile calculation.
