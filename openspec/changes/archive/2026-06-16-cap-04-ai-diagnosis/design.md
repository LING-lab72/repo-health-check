## Context

cap-03 完成后，分析报告返回 `{health_score, badge_level, dimensions[]}`，但缺少针对性的改进指导。LLM 诊断模块利用大模型的理解能力，将结构化数据转化为自然语言的改进建议。

## Goals / Non-Goals

**Goals:**
- 接入 OpenAI / DeepSeek API，生成 3-5 条改进建议
- 每条建议结构化：severity（high/medium/low）+ estimated_hours + confidence
- confidence < 70 标记 need_human_review
- API key 通过 .env 环境变量配置

**Non-Goals:**
- 不支持其他 LLM 提供商（Claude/Gemini 等）
- 不实现流式响应（SSE）
- 不做 Fine-tuning 或 RAG

## Decisions

### 1. LLM Provider：优先 DeepSeek，兼容 OpenAI

**选择**：检测环境变量优先级 `DEEPSEEK_API_KEY > OPENAI_API_KEY`，自动选择 provider。DeepSeek 使用 `https://api.deepseek.com/v1`，OpenAI 使用 `https://api.openai.com/v1`。

**理由**：DeepSeek 成本更低（约 OpenAI 1/10），中文支持好，适合本项目场景。OpenAI 作为备选保证兼容性。

**备选**：仅支持 DeepSeek → 限制了用户选择。支持所有 provider → 复杂度高，当前不需要。

### 2. 调用方式：httpx 异步调用

**选择**：用 httpx 的 `AsyncClient` 发送 POST 到 `/chat/completions`，30s 超时。API 调用失败时降级为本地规则诊断。

**理由**：httpx 兼容 FastAPI 的 async 生态。降级保证无 API key 时服务依然可用。

### 3. Prompt 设计：结构化 JSON 输出

**选择**：System prompt 指导模型基于 `{dimension_scores, issues}` 生成 JSON 数组 `[{advice, severity, estimated_hours, confidence}]`。JSON 输出比自由文本更可靠。

**理由**：JSON 便于后端解析和前端展示。Prompt 中明确 schema 约束输出格式。

### 4. 集成方式：aggregator 中调用，非单独端点

**选择**：在 `aggregate()` 完成后异步调用 `ai_diagnose()`，结果注入返回 dict 的 `ai_diagnosis` 字段。AI 诊断失败不影响主流程。

**理由**：保持 API 简洁（一次请求获取完整报告），AI 作为增值功能不阻塞核心分析。

### 5. API Key 配置：python-dotenv + os.environ

**选择**：在主入口或 CI 中通过 `load_dotenv()` 加载 `.env`，诊断模块通过 `os.environ.get("DEEPSEEK_API_KEY")` 读取。

**理由**：.env 是 Python 社区标准，不引入额外配置系统。

## Risks / Trade-offs

- **[LLM 调用超时]** 10-30s → httpx 30s timeout，超时后降级为本地规则
- **[API key 泄露]** .env 误提交 → .gitignore 已排除 .env
- **[幻觉建议]** 模型可能给出不合理建议 → confidence < 70 标记 need_human_review，由用户最终判断
- **[API 成本]** 每次分析 ~500 tokens → DeepSeek 价格极低（~¥0.001/次），可接受
