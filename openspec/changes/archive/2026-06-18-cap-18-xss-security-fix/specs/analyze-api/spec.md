# Analyze API

## Purpose

提供 POST /api/analyze 分析端点、GET 状态查询端点、GET /api/leaderboard 排行榜端点，以及 HTML 报告导出端点。导出端点包含 XSS 防护和 Content-Disposition 头注入防护。

## Requirements

### Requirement: 分析报告 API

系统 SHALL 在 POST /api/analyze 端点接受 `repo_url` 参数，执行 6 维度分析并返回 JSON 结果。

### Requirement: HTML 报告导出

系统 SHALL 在 GET /api/export/{repo_hash} 端点生成可下载的 HTML 报告文件。

#### Scenario: 正常导出
- **WHEN** 客户端请求已分析仓库的 HTML 报告
- **THEN** 返回 Content-Type: text/html 响应，Content-Disposition: attachment 触发浏览器下载

#### Scenario: XSS 防护
- **WHEN** 动态字段（repo_url、dimension、advice、severity、badge_level、analyzed_at）包含 HTML 特殊字符
- **THEN** 系统 SHALL 使用 `html.escape(text, quote=True)` 对所有动态字段进行 HTML 转义后再插入 HTML 模板，防止存储型 XSS 攻击

#### Scenario: Content-Disposition 头注入防护
- **WHEN** 仓库 URL 包含特殊字符（如 `\r`, `\n`, `"`）
- **THEN** 系统 SHALL 仅允许文件名中包含安全字符集 `[a-zA-Z0-9\-._]`，其余字符替换为 `_`，防止 HTTP 头注入
