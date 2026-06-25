# Badge API

## Purpose

生成 shields.io 风格 SVG 徽章，支持嵌入 GitHub README。包含 XSS 防护层。

## Requirements

### Requirement: Badge SVG 生成

系统 SHALL 在 GET /api/badge/{repo_hash} 端点生成 shields.io 风格 SVG 徽章，包含 label（如 "health"）和 value（如 "82/100"），颜色根据分数等级变化。

#### Scenario: 正常请求
- **WHEN** 客户端请求已分析仓库的 Badge
- **THEN** 返回 SVG 格式响应，Content-Type 为 image/svg+xml

#### Scenario: XSS 防护
- **WHEN** label 或 value 包含 HTML 特殊字符（如 `<`, `>`, `"`, `&`）
- **THEN** 系统 SHALL 使用 `html.escape(text, quote=True)` 对动态文本进行 HTML 转义后再插入 SVG 模板，防止 SVG 注入攻击

### Requirement: 未分析仓库提示

系统 SHALL 在请求未分析仓库的 Badge 时返回默认灰色 SVG（label="health", value="pending"）。
