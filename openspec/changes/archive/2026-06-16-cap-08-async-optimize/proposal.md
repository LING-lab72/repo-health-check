## Why

cap-07 后项目已完整，但存在三个待优化点：aggregate/ai_diagnose 使用了 sync wrapper 导致 asyncio.run() 冲突；vercel.json 缺少 SPA fallback；compare API 为 GET 请求不标准。

## What Changes

- aggregate() 改为 async，直接 await ai_diagnose()，删除 sync_diagnose
- analyze.py / compare.py 改为 await aggregate()
- compare API 从 GET 改为 POST + Pydantic model
- badge API 添加 storage fallback（cache miss → 查 history.json）
- vercel.json 添加 SPA fallback 规则

## Capabilities

### Modified Capabilities
- `analysis-aggregator`: async aggregate + 直接 await AI
- `compare-mode`: POST 请求 + Pydantic
- `badge-api`: storage fallback 三级查找
- `deploy-config`: SPA fallback

### Removed
- `sync_diagnose` 函数（不再需要）
