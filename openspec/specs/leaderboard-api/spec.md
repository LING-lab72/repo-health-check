# Leaderboard API

## Purpose

排行榜 API 和前端页面，展示已分析仓库的按健康分排名。

## Requirements

### Requirement: 排行榜 API

系统 SHALL 提供 GET /api/leaderboard 端点，返回缓存中所有仓库按 health_score 降序排列。

### Requirement: 排行榜页面

系统 SHALL 在 LeaderboardPage 展示排行列表，前三名有金银铜视觉效果。
