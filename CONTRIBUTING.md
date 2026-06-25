# Contributing

Thanks for helping improve Repo Health Check.

## Local Setup

```bash
pip install -r backend/requirements.txt pytest
cd frontend && npm install
```

Create `.env` from `.env.example` and set `SESSION_SECRET`.

## Checks

```bash
pytest backend/tests -q
cd frontend && npm run lint && npm test -- --run && npm run build
```

Use Conventional Commits, for example `feat: add repository baseline chart`.

## Pull Requests

- Keep changes focused and include tests for behavior changes.
- Update documentation when configuration, deployment, or user-visible behavior changes.
- Do not commit local runtime files such as `.env`, `data/*.db`, `node_modules`, or `dist`.
