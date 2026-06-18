# Repo Health Check

> One-click health check for your GitHub repositories — 6-dimension analysis, radar charts, AI diagnostics, health badges, and leaderboard

[中文](./README.md) | **English**

## Features

- **6-Dimension Radar Chart**: Code Quality / Test Coverage / Architecture Health / Documentation Completeness / Dependency Security / Engineering Standards
- **AI Smart Diagnostics**: Powered by DeepSeek / OpenAI, generates 3-5 targeted improvement suggestions
- **Health Badges**: shields.io-style SVG badges embeddable in README
- **Leaderboard**: Multi-repo comparison + voting + trend tags
- **Compare Mode**: Side-by-side dual-repo radar chart comparison
- **History Trends**: Line charts showing score changes across multiple analyses
- **Theme Toggle**: Dark/Light dual themes
- **Share Results**: One-click copy of analysis report links
- **Report Export**: Printable HTML reports
- **GitHub OAuth**: User-level vote deduplication after login
- **Smart Networking**: Direct → Proxy → Friendly prompt, 3-level automatic fallback. No manual proxy configuration needed in China
- **OpenSpec Standardization**: All changes archived via capability management, specs directory continuously maintained

## Screenshots

### Home

Dark immersive interface with Iridescence WebGL background + CurvedLoop animated title + health score entry.

![Home](docs/screenshots/home.png)

### Analysis Report

6-dimension radar chart + AI diagnostic suggestions + health badge + history trend chart, glassmorphism card design.

![Report](docs/screenshots/report.png)

### Leaderboard

Multi-repo health score comparison with voting and trend tags.

![Leaderboard](docs/screenshots/leaderboard.png)

### Compare Mode

Side-by-side dual-repo radar chart comparison for intuitive difference visualization.

![Compare](docs/screenshots/compare.png)

### About

Project introduction, SDD development workflow, and contribution guidelines.

![About](docs/screenshots/about.png)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Git

### Local Run

```bash
git clone https://github.com/LING-lab72/repo-health-check
cd repo-health-check

# Backend
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

#### Network Environment in China

When using in China, the backend has a built-in proxy auto-fallback mechanism:

1. First attempts direct connection to GitHub
2. On direct connection failure, auto-detects `GIT_HTTP_PROXY` from `.env` and attempts proxy
3. Returns a friendly error message if proxy is unreachable

To manually specify a proxy, pass environment variables at startup:

```bash
GIT_HTTP_PROXY=http://127.0.0.1:7890 \
  http_proxy=http://127.0.0.1:7890 \
  https_proxy=http://127.0.0.1:7890 \
  uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

You can also configure `GIT_HTTP_PROXY=http://127.0.0.1:7890` in `.env`, the backend will read it automatically.

### Docker Deployment

```bash
docker-compose up -d
# Frontend: http://localhost
# Backend: http://localhost:8000
```

### Configuration

```bash
cp .env.example .env
# Edit .env to fill in API Key, OAuth credentials, and proxy address
```

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key (recommended) | — |
| `OPENAI_API_KEY` | OpenAI API Key (alternative) | — |
| `GIT_HTTP_PROXY` | Git HTTP proxy address | `http://127.0.0.1:7890` |
| `GITHUB_CLIENT_ID` | GitHub OAuth Client ID | — |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth Client Secret | — |
| `CORS_ORIGINS` | CORS allowed origins | `http://localhost:5173` |
| `SESSION_SECRET` | Session signing secret | — |

## Scoring Dimensions

| Dimension | Weight | Tools |
|-----------|--------|-------|
| Code Quality | 20% | radon (CC+MI) + ESLint |
| Test Coverage | 20% | Test file ratio + framework detection + lcov parsing |
| Architecture Health | 15% | God Class + import coupling + madge circular dependencies |
| Documentation Completeness | 15% | README quality + comment density |
| Dependency Security | 15% | bandit scanning + pip-audit |
| Engineering Standards | 15% | CI/Linter/License/Git conventions |

## Project Structure

```
repo-health-check/
├── backend/
│   ├── main.py              # FastAPI entry
│   ├── routes/              # API routes (analyze, badge, auth, compare, export, history, leaderboard, vote)
│   ├── analyzer/            # 6-dimension analysis engine (code_quality, test_coverage, architecture, documentation, dependency_security, engineering)
│   ├── ai/                  # AI diagnostics module (DeepSeek / OpenAI)
│   ├── models/              # Data models
│   ├── services/            # Core services (clone, cache, storage, session)
│   └── tests/               # pytest tests
├── frontend/
│   └ src/
│   │  ├── pages/            # 5 pages (Home, Report, Leaderboard, Compare, About)
│   │  ├── components/       # Components (Navbar, RadarChart, ScoreBar, HistoryChart)
│   │  └── api.ts            # API call layer
│   └ vite.config.ts
│   └ package.json
├── sdd/                     # SDD scoring rule definitions
├── openspec/                # OpenSpec engineering specification management
│   ├── project.md           # Project overview
│   ├── specs/               # Capability domain specs (9)
│   └ changes/archive/       # Archived capabilities (15)
├── data/                    # Runtime data (history.json, etc.)
├── .env                     # Environment variable configuration
├── docker-compose.yml       # Docker deployment
└── README.md
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+ / FastAPI / uvicorn |
| Analysis Engine | radon / lizard / bandit / pip-audit / ESLint / madge |
| AI Diagnostics | OpenAI / DeepSeek API |
| Frontend | React 18 / TypeScript / Vite / ECharts |
| Authentication | GitHub OAuth + itsdangerous session |
| Storage | JSON file + in-memory cache (TTL 30min) |
| Engineering Management | OpenSpec (capability archive + specs) |
| Deployment | Docker Compose |

## Networking & Cache Mechanism

### Git Clone Auto-Fallback

The backend `clone.py` implements a 3-level auto-fallback strategy:

1. **Direct Probe**: First tests GitHub direct connectivity via `git ls-remote` (explicitly `-c http.proxy=""` to bypass global proxy config)
2. **Proxy Fallback**: On direct failure, detects `GIT_HTTP_PROXY` from `.env` or startup env vars, checks proxy port reachability via socket, then clones with `git -c http.proxy=... -c https.proxy=...` flags
3. **Friendly Prompt**: Returns a user-friendly message instead of raw SSL/TLS errors when proxy is unavailable

### Cache Strategy

- Successful results cached for 30 minutes, returned directly on cache hit
- **Error results don't block re-detection**: When cache is hit but contains an `_error` field, it automatically `invalidate()`s and re-executes the actual detection, ensuring normal operation after network recovery

## OpenSpec Standardization

This project uses OpenSpec for engineering specification management:

- `openspec/specs/` — 9 capability domain continuously maintained specs
- `openspec/changes/archive/` — 15 archived completed capabilities

Each capability archive includes: proposal (motivation & scope), design (technical decisions), tasks (task list), .openspec.yaml (metadata), and affected specs snapshots.

### Recent Capabilities

| ID | Name | Description |
|----|------|-------------|
| cap-12 | bugfix-quality | Multiple bug fixes and quality improvements |
| cap-13 | quality-polish | Detail polishing |
| cap-14 | proxy-auto-degrade-and-cache-fix | Proxy auto-fallback + error cache non-blocking |
| cap-15 | curved-loop-hero-title | CurvedLoop curved title integration on homepage |

## Testing

```bash
pytest backend/tests/ -v          # Backend unit tests
cd frontend && npm test           # Frontend tests
```

## Contributing

Commit conventions follow [Conventional Commits](https://www.conventionalcommits.org/).

```bash
git checkout -b feature/your-feature
git commit -m 'feat: add your feature'
git push origin feature/your-feature
```

Visit the About page to learn about the SDD development workflow and contribution guidelines.

## License

MIT
