# Report Export

## Purpose

Provide a downloadable, self-contained repository health report that is useful for sharing outside the web app.

## Requirements

### Requirement: HTML Report

The system SHALL provide `GET /api/export/{repo_hash}` and return a downloadable HTML report for a cached or persisted analysis result.

#### Scenario: Visual report includes radar chart
- **WHEN** a report has at least three dimensions
- **THEN** the exported HTML SHALL include a static inline SVG radar chart generated from dimension scores

#### Scenario: Visual report includes score table
- **WHEN** a report has dimensions
- **THEN** the exported HTML SHALL include a score table with bounded score bar widths

#### Scenario: AI diagnosis included
- **WHEN** a report contains `ai_diagnosis`
- **THEN** the exported HTML SHALL render each suggestion with severity, confidence, and estimated effort

### Requirement: Export Safety

All dynamic report fields SHALL be escaped or bounded before insertion into HTML, SVG, CSS width, filename, or header contexts.

#### Scenario: Untrusted dimension label
- **WHEN** a dimension label contains HTML markup
- **THEN** the exported radar chart and score table SHALL render escaped text and not executable markup

#### Scenario: Untrusted numeric value
- **WHEN** a score, confidence, or estimated hour value is outside the allowed range
- **THEN** the exported report SHALL clamp that value before using it in text or style attributes

### Requirement: Browser PDF Export

The report page SHALL provide a PDF export action without requiring server-side PDF generation.

#### Scenario: Export PDF from report page
- **WHEN** the user clicks the PDF export action
- **THEN** the frontend SHALL fetch the HTML report, open a printable document, and trigger the browser print dialog so the user can save it as PDF

### Requirement: Share Card Image

The report page SHALL provide a share card generator that downloads a PNG image summarizing the report.

#### Scenario: Generate share card
- **WHEN** an analysis result is available and the user clicks the share-card action
- **THEN** the frontend SHALL render repository name, score, badge level, radar summary, and language mix to a canvas and download it as PNG

### Requirement: Language Distribution Visualization

The report page SHALL visualize repository language distribution when analyzer data is available.

#### Scenario: Code quality language breakdown
- **WHEN** `code_quality.details.language_breakdown` contains positive language counts
- **THEN** the frontend SHALL render those counts as a language distribution pie chart

#### Scenario: Missing language breakdown
- **WHEN** no language breakdown data is available
- **THEN** the frontend SHALL show a stable empty state instead of a blank chart

### Requirement: Wrapped-Style Share Poster

The report share card SHALL use a branded Wrapped-style layout suitable for social sharing.

#### Scenario: Peer percentile message
- **WHEN** an analysis result is available
- **THEN** the generated share card SHALL include a percentile message such as `超过 90% 的 JavaScript/TypeScript 项目`, derived from score and dominant language
