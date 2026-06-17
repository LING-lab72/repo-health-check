## ADDED Requirements

### Requirement: 排行榜 API

系统 SHALL 提供 GET /api/leaderboard 端点，返回缓存中所有已完成分析仓库的排行，按 health_score 降序。

#### Scenario: 返回排行

- **WHEN** 缓存中有 5 个分析结果
- **THEN** 返回 5 条记录，按 health_score 降序，每条含 repo_url / health_score / badge_level

#### Scenario: 空缓存

- **WHEN** 缓存为空
- **THEN** 返回空数组，HTTP 200

### Requirement: 排行榜页面

系统 SHALL 在 LeaderboardPage 调用 GET /api/leaderboard，展示排行列表，每行显示排名、仓库名、健康分、Badge 等级。

#### Scenario: 排行展示

- **WHEN** 排行榜返回数据
- **THEN** 页面渲染排行列表，前三名有金银铜视觉效果
