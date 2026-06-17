## MODIFIED Requirements

### Requirement: POST 分析端点

系统 SHALL 提供 POST /api/analyze 端点，接收 JSON body `{"repo_url": "..."}`，执行 clone → 分析 → 聚合 → AI 诊断流程，返回完整健康报告。

#### Scenario: 正常分析请求

- **WHEN** POST /api/analyze `{"repo_url": "https://github.com/psf/requests"}`
- **THEN** HTTP 200，返回 `{"code": 0, "message": "success", "data": {..., "health_score": ..., "badge_level": "A", "dimensions": [...], "ai_diagnosis": [...]}}`

## ADDED Requirements

### Requirement: 排行榜端点

系统 SHALL 提供 GET /api/leaderboard 端点，返回缓存中所有仓库按 health_score 降序排列的列表。

#### Scenario: 返回排行

- **WHEN** GET /api/leaderboard
- **THEN** 返回 `[{"repo_url": ..., "health_score": ..., "badge_level": ...}, ...]` 数组
