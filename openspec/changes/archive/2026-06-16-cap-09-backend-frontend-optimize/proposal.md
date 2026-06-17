## Why

cap-08 后仍有细节优化空间：分析请求需支持异步后台模式、投票需防刷、CORS 需可配置、图表需响应式适配。

## What Changes

- POST /api/analyze 支持 `force_sync=false` 后台任务模式 + 前端轮询
- vote API 添加 IP 级 60s 冷却防刷
- ComparePage 维度匹配修复（名称匹配替代下标）
- CORS origins 从环境变量读取
- RadarChart / HistoryChart 添加 window resize 自适应

## Capabilities

### Modified Capabilities
- `analyze-api`: BackgroundTasks 异步模式 + 状态查询完善
- `vote-system`: IP 级速率限制
- `compare-mode`: 维度名称匹配
- `backend-main`: CORS 环境变量配置
- `frontend-real-api`: 轮询模式 + 图表自适应 + 429 错误处理
