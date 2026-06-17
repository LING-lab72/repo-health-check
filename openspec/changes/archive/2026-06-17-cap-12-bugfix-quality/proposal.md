## Why

cap-10/11 后发现多个 bug 和质量问题：HomePage 误判异步模式、Badge hash 算法不一致、Vercel 部署硬编码、vote API 格式不统一、session 硬编码密钥、flake8 20+ lint 问题。

## What Changes

- 修复 HomePage 异步模式误判错误
- Badge hash 前后端统一为 SHA-256
- Vercel 部署改用环境变量 API_BASE
- vote API 改为 POST body
- export 添加 storage fallback
- session SECRET 从环境变量读取
- 修复全部 flake8 问题（0 issues）

## Capabilities

### Modified Capabilities
- `frontend-real-api`: HomePage 修复 + hash 统一 + API_BASE
- `vote-system`: POST body
- `badge-api`: hash 一致
- `export`: storage fallback
- `session`: 环境变量密钥
