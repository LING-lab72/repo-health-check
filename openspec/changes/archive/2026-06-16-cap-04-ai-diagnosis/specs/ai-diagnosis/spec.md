## ADDED Requirements

### Requirement: LLM 诊断调用

系统 SHALL 支持调用 OpenAI 或 DeepSeek Chat Completions API，基于六维分析指标生成改进建议。

#### Scenario: DeepSeek 优先

- **WHEN** 环境变量 DEEPSEEK_API_KEY 存在
- **THEN** 使用 DeepSeek API 生成诊断建议

#### Scenario: OpenAI 备选

- **WHEN** DEEPSEEK_API_KEY 不存在但 OPENAI_API_KEY 存在
- **THEN** 使用 OpenAI API 生成诊断建议

#### Scenario: 无 API Key 降级

- **WHEN** 两个 API key 均不存在
- **THEN** 返回本地规则诊断建议，不调用 LLM

### Requirement: 结构化建议输出

系统 SHALL 生成 3-5 条结构化改进建议，每条 MUST 包含 advice / severity / estimated_hours / confidence。

#### Scenario: 建议格式

- **WHEN** LLM 返回诊断结果
- **THEN** 每条建议为 `{"advice": "...", "severity": "high|medium|low", "estimated_hours": int, "confidence": 0-100}`

### Requirement: 置信度标记

系统 SHALL 对 confidence < 70 的建议自动标记 `need_human_review: true`。

#### Scenario: 低置信度标记

- **WHEN** LLM 返回建议 `{"confidence": 55, ...}`
- **THEN** 最终输出包含 `"need_human_review": true`

#### Scenario: 高置信度不标记

- **WHEN** LLM 返回建议 `{"confidence": 85, ...}`
- **THEN** 最终输出 `"need_human_review": false`

### Requirement: API 调用超时降级

系统 SHALL 设置 30 秒 LLM API 超时，超时时降级为本地规则诊断。

#### Scenario: 超时降级

- **WHEN** LLM API 调用超过 30 秒
- **THEN** 返回本地规则诊断结果，标记 `source: "fallback"`

### Requirement: 响应集成

系统 SHALL 在 POST /api/analyze 响应的 `data.ai_diagnosis` 字段中包含 AI 诊断结果。

#### Scenario: 正常响应含诊断

- **WHEN** POST /api/analyze 成功
- **THEN** 响应 data 包含 `ai_diagnosis` 字段，值为建议数组
