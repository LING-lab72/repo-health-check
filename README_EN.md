# Repo Health Check

> A GitHub repository health scanner with six-dimension analysis, AI diagnosis, badges, leaderboard, repository PK, exports, and share posters.

[中文](./README.md) | **English**

## Highlights

- **Six-dimension analysis**: code quality, test coverage, architecture, documentation, dependency security, and engineering hygiene.
- **AI diagnosis**: uses DeepSeek/OpenAI when configured; automatically falls back to local rule-based diagnosis without an API key.
- **Cache-aware reports**: cached results within 30 minutes skip clone/re-analysis.
- **Visual reports**: radar chart, score bars, language distribution pie chart, history trend, and peer benchmark line.
- **Export and sharing**: HTML report, browser PDF export, Wrapped-style share card.
- **Repository PK Arena**: compare two repositories with animated health bars and downloadable PK poster.
- **Leaderboard**: SQLite persistence, pagination, voting cooldown, and trend labels.
- **Security hardening**: HTML/SVG escaping, strong session secret, OAuth state validation, CORS allowlist.
- **Engineering workflow**: GitHub Actions, pytest, Vitest, OpenSpec archives, and one-click Windows launcher.

## Screenshots

### Home

![Home](docs/screenshots/home.png)

### Report

![Report](docs/screenshots/report.png)

### Repository PK

![Repository PK](docs/screenshots/compare.png)

### Leaderboard

![Leaderboard](docs/screenshots/leaderboard.png)

### About

![About](docs/screenshots/about.png)

## Quick Start

### One-click launcher on Windows

Double-click:

```text
Start-RepoHealth.bat
```

It starts:

- Backend: `http://127.0.0.1:8002`
- Frontend: `http://127.0.0.1:5174`

### Manual start

Requirements:

- Python 3.11+
- Node.js 20+
- Git

Backend:

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002 --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open:

```text
http://127.0.0.1:5174
```

## Configuration

```bash
cp .env.example .env
```

| Variable | Description | Default/example |
| --- | --- | --- |
| `SESSION_SECRET` | Session signing secret, required outside tests | required |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5174,http://127.0.0.1:5174,...` |
| `FRONTEND_URL` | OAuth callback redirect target | `http://localhost:5174` |
| `DEEPSEEK_API_KEY` | Optional DeepSeek API key | empty |
| `OPENAI_API_KEY` | Optional OpenAI API key | empty |
| `GIT_HTTP_PROXY` | Optional Git clone proxy | `http://127.0.0.1:7890` |
| `TRUST_PROXY_HEADERS` | Trust `X-Forwarded-For` for voting identity | `false` |
| `ALLOW_NPX_INSTALL` | Allow npx to install missing tools online | `0` |

No API key is required for diagnosis. The system falls back to local rule-based suggestions automatically.

## Project Structure

```text
repo-health-check/
├─ backend/                # FastAPI API, analyzers, services, tests
├─ frontend/               # React/Vite UI, charts, share-card utilities
├─ docs/screenshots/       # README screenshots
├─ openspec/               # Specs and archived capabilities
├─ data/                   # SQLite runtime data
├─ Start-RepoHealth.bat    # Windows launcher
└─ README.md
```

## Testing

Backend:

```bash
python -m pytest backend/tests
```

Frontend:

```bash
cd frontend
npm run lint
npm test -- --run
npm run build
```

## OpenSpec

OpenSpec artifacts live in:

- `openspec/specs/`
- `openspec/changes/archive/`

Recent capabilities:

- `cap-19-security-architecture-hardening`
- `cap-20-report-leaderboard-ux`

## Contributing

See:

- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [SECURITY.md](./SECURITY.md)
- [CHANGELOG.md](./CHANGELOG.md)

## License

MIT
