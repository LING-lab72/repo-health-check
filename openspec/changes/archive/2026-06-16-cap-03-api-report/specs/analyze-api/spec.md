## ADDED Requirements

### Requirement: POST 分析端点

系统 SHALL 提供 POST /api/analyze 端点，接收 JSON body `{"repo_url": "..."}`，执行 clone → 分析 → 聚合流程，返回完整健康报告。

#### Scenario: 正常分析请求

- **WHEN** POST /api/analyze `{"repo_url": "https://github.com/psf/requests"}`
- **THEN** HTTP 200，返回 `{"code": 0, "message": "success", "data": {..., "health_score": ..., "badge_level": "A", "dimensions": [...]}}`

#### Scenario: 无效 repo_url

- **WHEN** POST /api/analyze `{"repo_url": "not-a-url"}`
- **THEN** HTTP 400，返回 `{"code": 400, "message": "Invalid repository URL", "data": null}`

#### Scenario: 克隆失败

- **WHEN** POST /api/analyze `{"repo_url": "https://github.com/nonexistent/repo"}`
- **THEN** HTTP 400，返回 `{"code": 400, "message": "Failed to clone repository", "data": null}`

### Requirement: 请求格式校验

系统 SHALL 校验 POST body 中 repo_url 字段存在且为合法 GitHub URL（以 github.com 开头）。

#### Scenario: 缺少字段

- **WHEN** POST /api/analyze `{}`
- **THEN** HTTP 422，返回校验错误

### Requirement: GET 任务状态查询

系统 SHALL 提供 GET /api/analyze/status?task_id=xxx 端点，返回分析任务状态。

#### Scenario: 查询缓存结果

- **WHEN** GET /api/analyze/status?task_id=<valid_hash>
- **THEN** 返回对应仓库的分析状态（cached/pending/not_found）
