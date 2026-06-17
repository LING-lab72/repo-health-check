## MODIFIED Requirements

### Requirement: POST 分析端点

系统 SHALL 提供 POST /api/analyze 端点，接收 JSON body `{"repo_url": "..."}`，执行 clone → 分析 → 聚合流程，返回完整健康报告，包含 `ai_diagnosis` 字段。

#### Scenario: 正常分析请求

- **WHEN** POST /api/analyze `{"repo_url": "https://github.com/psf/requests"}`
- **THEN** HTTP 200，返回 `{"code": 0, "message": "success", "data": {..., "health_score": ..., "badge_level": "A", "dimensions": [...], "ai_diagnosis": [...]}}`

#### Scenario: 无效 repo_url

- **WHEN** POST /api/analyze `{"repo_url": "not-a-url"}`
- **THEN** HTTP 400，返回 `{"code": 400, "message": "Invalid repository URL", "data": null}`

#### Scenario: 克隆失败

- **WHEN** POST /api/analyze `{"repo_url": "https://github.com/nonexistent/repo"}`
- **THEN** HTTP 400，返回错误信息
