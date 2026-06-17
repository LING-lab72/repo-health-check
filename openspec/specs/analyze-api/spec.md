# Analyze API

## Purpose

提供仓库健康分析的 HTTP API 端点，串联 git clone → 分析聚合 → AI 诊断 → 缓存 → 响应的完整流程。排行榜通过 GET /api/leaderboard 获取。

## Requirements

### Requirement: POST 分析端点

系统 SHALL 提供 POST /api/analyze 端点，接收 JSON body `{"repo_url": "...", "force_sync": false, "skip_ai": false}`，对 repo_url 使用 `cache.normalize_url()` 规范化后执行 clone → 分析 → 聚合 → 缓存流程。async 模式（force_sync=false）响应 data SHALL 包含 `repo_url` 字段供前端回传给 status 端点。当缓存命中且结果包含 `_error` 字段时，SHALL 先调用 `cache.invalidate(repo_url)` 清除错误缓存，再继续执行实际检测，确保网络恢复后可重新检测。

#### Scenario: 缓存命中成功结果
- **WHEN** POST /api/analyze 且缓存中存在成功结果（无 `_error`）
- **THEN** 直接返回缓存结果，响应 code=0

#### Scenario: 缓存命中错误结果——清除后重新检测
- **WHEN** POST /api/analyze 且缓存中存在错误结果（含 `_error` 字段）
- **THEN** 清除该错误缓存条目，继续执行 clone → 分析流程

#### Scenario: 正常分析请求（sync）
- **WHEN** POST /api/analyze `{"repo_url": "https://github.com/user/repo.git", "force_sync": true, "skip_ai": true}`
- **THEN** URL 被规范化为 `"https://github.com/user/repo"`，克隆并分析后缓存 key 为规范化 URL

#### Scenario: Async 模式响应包含 repo_url
- **WHEN** POST /api/analyze `{"repo_url": "https://github.com/user/repo", "force_sync": false}`
- **THEN** 返回 `{"code": 1, "data": {"task_id": "...", "repo_url": "https://github.com/user/repo", "status": "pending"}}`

### Requirement: 请求格式校验

系统 SHALL 校验 POST body 中 repo_url 字段存在且为合法 GitHub URL。

### Requirement: GET 任务状态查询

系统 SHALL 提供 GET /api/analyze/status 端点。当传入 `repo_url` 参数时，SHALL 使用精确缓存查询（`cache.get(repo_url)` 或 `cache.get_by_hash(task_id, repo_url)`）；未传入 `repo_url` 时，SHALL 使用哈希遍历回退（兼容旧客户端）。

#### Scenario: 精确 repo_url 查询
- **WHEN** GET /api/analyze/status?task_id=abc123&repo_url=https://github.com/user/repo
- **THEN** 使用 `normalize_url(repo_url)` 精确查找缓存，返回对应状态

#### Scenario: 向后兼容无 repo_url
- **WHEN** GET /api/analyze/status?task_id=abc123
- **THEN** 使用哈希遍历回退查找缓存（保持旧行为）

### Requirement: 排行榜端点

系统 SHALL 提供 GET /api/leaderboard 端点，返回缓存中所有仓库按 health_score 降序排列的列表。
