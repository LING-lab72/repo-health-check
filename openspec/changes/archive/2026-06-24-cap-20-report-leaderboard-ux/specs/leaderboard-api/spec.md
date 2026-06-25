# Leaderboard API

## Purpose

排行榜 API 和前端页面，展示已分析仓库的按健康分排名。

## Requirements

### Requirement: 排行榜 API

系统 SHALL 提供 GET /api/leaderboard 端点，返回 SQLite 持久化存储中每个仓库最新一次分析结果，并按 health_score 降序排列。每条记录 SHALL 包含投票数 `_votes` 和趋势 `_trend`。

#### Scenario: 最新结果排名
- **WHEN** 同一 repo_url 有多条历史分析记录
- **THEN** 排行榜仅展示 analyzed_at 最新的一条记录

#### Scenario: 趋势标记
- **WHEN** 同一 repo_url 至少有两条历史记录
- **THEN** 排行榜根据最近两次 health_score 返回 `up`、`down` 或 `same`

### Requirement: 投票 API

系统 SHALL 提供 POST /api/vote 端点，校验 repo_url 为合法 GitHub URL，并使用登录用户 ID 或客户端标识作为 voter_id 进行投票冷却控制。

#### Scenario: 非法 URL 拒绝
- **WHEN** POST /api/vote body 中 repo_url 不是合法 GitHub 仓库 URL
- **THEN** 返回 HTTP 400

#### Scenario: 可信代理头
- **WHEN** 未设置 `TRUST_PROXY_HEADERS=true`
- **THEN** 系统 SHALL 不信任客户端提供的 `X-Forwarded-For` 作为投票身份来源

### Requirement: 排行榜页面

系统 SHALL 在 LeaderboardPage 展示排行列表，前三名有金银铜视觉效果。

### Requirement: Paginated Leaderboard

The system SHALL support paginated leaderboard reads through `GET /api/leaderboard?page=<n>&page_size=<n>`.

#### Scenario: Paginated response shape
- **WHEN** the request includes `page`
- **THEN** the response data SHALL be an object containing `items`, `total`, `page`, `page_size`, and `has_next`

#### Scenario: Legacy response compatibility
- **WHEN** the request omits `page`
- **THEN** the response data SHALL remain the legacy array of leaderboard items

#### Scenario: Page ranking offset
- **WHEN** LeaderboardPage renders page 2 with page size 20
- **THEN** the first displayed rank SHALL be 21
