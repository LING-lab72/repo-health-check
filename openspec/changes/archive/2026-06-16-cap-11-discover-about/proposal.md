## Why

提升用户首次体验和社区参与度：提供示例仓库快捷入口快速试用、排行榜趋势指示、项目关于页面。

## What Changes

- HomePage 添加知名开源项目快捷按钮
- LeaderboardPage 添加分数变化趋势标签（↑/↓/NEW）
- AboutPage 展示技术栈 + SDD 迭代 + 贡献方式
- storage.get_all() 添加 _trend 字段计算

## Capabilities

### New Capabilities
- `about-page`: 项目介绍 + 技术栈 + SDD 流程 + 贡献指引

### Modified Capabilities
- `leaderboard-api`: 趋势字段
- `frontend-real-api`: 快捷入口 + 趋势显示
