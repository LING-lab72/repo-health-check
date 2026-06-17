## Why

cap-03 已实现完整的健康分析报告（六维评分 + Badge），但用户得到的只是数字和 issues 列表，缺乏可操作的改进指导。引入 LLM 诊断模块，基于六维评分数据生成 3-5 条针对性改进建议，每条附带严重程度、预估修复时间和置信度，让体检报告从"发现问题"升级为"指导改进"。

## What Changes

- 新增 `backend/ai/` 包，含 `diagnose.py` LLM 诊断引擎
- 调用 OpenAI / DeepSeek API，根据六维指标生成结构化改进建议
- 每条建议含 severity / estimated_hours / confidence 字段
- confidence < 70 自动标记 need_human_review
- 在 POST /api/analyze 响应的 `ai_diagnosis` 字段中返回
- .env 中配置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY
- 添加 httpx 到 requirements.txt

## Capabilities

### New Capabilities
- `ai-diagnosis`: LLM 驱动的改进建议生成，基于六维健康指标输出结构化诊断报告

### Modified Capabilities
- `analyze-api`: POST /api/analyze 响应新增 `ai_diagnosis` 字段
- `analysis-aggregator`: aggregate() 新增 ai_diagnosis 返回

## Impact

- 新增目录：`backend/ai/`
- 新增文件：`backend/ai/__init__.py`、`backend/ai/diagnose.py`
- 修改文件：`backend/analyzer/aggregator.py`（调用 AI 诊断）、`backend/requirements.txt`（+httpx）
- 新增依赖：httpx（HTTP 客户端）
- 新增环境变量：DEEPSEEK_API_KEY / OPENAI_API_KEY
