## MODIFIED Requirements

### Requirement: POST 分析端点

系统 SHALL 提供 POST /api/analyze 端点，接收 JSON body `{"repo_url": "...", "force_sync": false, "skip_ai": false}`，对 repo_url 使用 `cache.normalize_url()` 规范化后执行 clone → 分析 → 聚合 → 缓存流程。当缓存命中且结果包含 `_error` 字段时，SHALL 先调用 `cache.invalidate(repo_url)` 清除错误缓存，再继续执行实际检测，确保网络恢复后可重新检测。

#### Scenario: 缓存命中成功结果
- **WHEN** POST /api/analyze 且缓存中存在成功结果
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
