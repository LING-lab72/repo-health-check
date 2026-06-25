# Security Policy

## Reporting a Vulnerability

Please open a private security advisory on GitHub if available, or contact the maintainer directly before publishing details.

Include:

- Affected endpoint or component
- Reproduction steps
- Impact and suggested severity
- Suggested fix, if known

## Supported Configuration

Production deployments must set:

- `SESSION_SECRET`
- `CORS_ORIGINS`
- `FRONTEND_URL`
- `COOKIE_SECURE=true` when served over HTTPS

Only set `TRUST_PROXY_HEADERS=true` when the app is behind a trusted reverse proxy that overwrites forwarded headers.
