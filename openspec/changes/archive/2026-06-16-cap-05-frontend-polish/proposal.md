## Why

cap-01 搭建了前端骨架（HomePage / ReportPage / LeaderboardPage 占位），cap-03/04 实现了完整后端 API（/api/analyze、/api/badge、ai_diagnosis）。当前前端页面均为 mock 数据，需要接入真实 API，完成从输入 URL 到展示完整报告、雷达图、AI 诊断、Badge 嵌入代码的全流程。

## What Changes

- ReportPage：调用 POST /api/analyze，渲染 ECharts 雷达图、六维分数条、AI 诊断卡、问题列表
- HomePage：添加 loading 状态、URL 校验、错误 toast
- LeaderboardPage：调用后端排行榜 API（新增 GET /api/leaderboard）
- 报告页底部展示 Badge Markdown 嵌入代码
- 全局样式美化：暗色主题、CSS 动画过渡
- 新增后端 GET /api/leaderboard 端点（按健康分排序返回缓存中所有结果）

## Capabilities

### New Capabilities
- `frontend-real-api`: 前端接入真实分析 API，ECharts 雷达图、AI 诊断展示
- `leaderboard-api`: 排行榜 API + 前端页面
- `dark-theme`: 全局暗色主题 + 动画过渡

### Modified Capabilities
- `analyze-api`: 新增 GET /api/leaderboard 端点

## Impact

- 重写：`frontend/src/pages/HomePage.tsx`、`frontend/src/pages/ReportPage.tsx`、`frontend/src/pages/LeaderboardPage.tsx`
- 修改：`frontend/src/index.css`（暗色主题）
- 新增：`frontend/src/components/RadarChart.tsx`、`frontend/src/components/ScoreBar.tsx`
- 新增：`backend/routes/leaderboard.py`、修改 `backend/routes/__init__.py`
- 新增依赖：`@emotion/react`、`@emotion/styled`（可选动画库）
