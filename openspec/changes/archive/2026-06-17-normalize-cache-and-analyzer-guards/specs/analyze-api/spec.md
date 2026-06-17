## MODIFIED Requirements

### Requirement: GET 任务状态查询

系统 SHALL 提供 GET /api/analyze/status 端点。当传入 `repo_url` 参数时，SHALL 使用精确缓存查询（`cache.get(repo_url)` 或 `cache.get_by_hash(task_id, repo_url)`）；未传入 `repo_url` 时，SHALL 使用哈希遍历回退（兼容旧客户端）。端点 SHALL 返回分析任务状态。

#### Scenario: 精确 repo_url 查询
- **WHEN** GET /api/analyze/status?task_id=abc123&repo_url=https://github.com/user/repo
- **THEN** 使用 `normalize_url(repo_url)` 精确查找缓存，返回对应状态

#### Scenario: 向后兼容无 repo_url
- **WHEN** GET /api/analyze/status?task_id=abc123
- **THEN** 使用哈希遍历回退查找缓存（保持旧行为）

### Requirement: POST 分析端点

系统 SHALL 提供 POST /api/analyze 端点，接收 JSON body `{"repo_url": "...", "force_sync": false, "skip_ai": false}`，对 repo_url 使用 `cache.normalize_url()` 规范化后执行 clone → 分析 → 聚合 → 缓存流程。async 模式（force_sync=false）响应 data SHALL 包含 `repo_url` 字段供前端回传给 status 端点。

#### Scenario: 正常分析请求（sync）
- **WHEN** POST /api/analyze `{"repo_url": "https://github.com/user/repo.git", "force_sync": true, "skip_ai": true}`
- **THEN** URL 被规范化为 `"https://github.com/user/repo"`，克隆并分析后缓存 key 为规范化 URL

#### Scenario: Async 模式响应包含 repo_url
- **WHEN** POST /api/analyze `{"repo_url": "https://github.com/user/repo", "force_sync": false}`
- **THEN** 返回 `{"code": 1, "data": {"task_id": "...", "repo_url": "https://github.com/user/repo", "status": "pending"}}`
