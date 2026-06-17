## Why

cap-02 实现了 6 个分析器的真实逻辑，但 `/api/analyze` 仍是 mock 桩，无法端到端运行。本变更搭建完整的分析流水线：Git clone → 6 维分析 → 聚合评分 → API 返回结果 + Badge 生成，打通用户输入 GitHub URL 到获得健康报告的全链路。

## What Changes

- 新增 `backend/services/clone.py`：GitHub URL git clone --depth 1 到临时目录，60s 超时
- 新增 `backend/analyzer/aggregator.py`：调用 6 个 Analyzer，按 health-spec.yaml 权重聚合总分和 Badge 等级
- 重写 `backend/routes/analyze.py`：POST /api/analyze 接收 repo_url → clone → aggregator → 返回完整报告；GET /api/analyze/status 查询异步任务状态
- 新增 `backend/routes/badge.py`：GET /api/badge/{hash} 返回 shields.io 风格 SVG Badge
- 新增 `backend/services/cache.py`：内存 LRU 缓存，key=repo_url，30 分钟 TTL
- **BREAKING**：POST /api/analyze 请求格式从 query 参数改为 JSON body `{"repo_url": "..."}`

## Capabilities

### New Capabilities
- `repo-clone-service`: Git clone 服务，shallow clone、超时控制、临时目录管理
- `analysis-aggregator`: 分析聚合器，串行调用 6 个分析器按权重计算总分，输出 Badge 等级
- `analyze-api`: 重写的分析 API 端点，支持同步分析 + 异步任务查询
- `badge-api`: SVG Badge 生成端点，shields.io 风格，按健康等级着色
- `result-cache`: 结果缓存服务，内存 LRU，30 分钟过期

### Modified Capabilities
（无，此为新功能）

## Impact

- 新增目录：`backend/services/`
- 新增文件：`backend/services/clone.py`、`backend/analyzer/aggregator.py`、`backend/routes/badge.py`、`backend/services/cache.py`
- 重写文件：`backend/routes/analyze.py`
- 新增依赖：git 命令行工具（环境依赖，非 Python 包）
- API 变更：POST /api/analyze 请求格式从 query 参数改为 JSON body ⚠️ **BREAKING**
