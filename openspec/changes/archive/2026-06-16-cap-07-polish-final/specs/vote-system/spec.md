# Vote System

## Purpose

排行榜投票功能，用户可给仓库点赞，每周评选最健康仓库。

## Requirements

### Requirement: 投票 API

系统 SHALL 提供 POST /api/vote 端点，递增仓库票数并持久化。

### Requirement: 每周挑战

系统 SHALL 在排行榜顶部展示本周最健康仓库。
