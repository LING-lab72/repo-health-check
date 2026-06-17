## 1. 后端排行榜 API

- [x] 1.1 创建 `backend/routes/leaderboard.py`，实现 GET /api/leaderboard
- [x] 1.2 在 `backend/routes/__init__.py` 中注册 leaderboard 路由

## 2. ReportPage 真实数据渲染

- [x] 2.1 创建 `frontend/src/components/RadarChart.tsx` ECharts 雷达图组件
- [x] 2.2 创建 `frontend/src/components/ScoreBar.tsx` 六维分数条组件
- [x] 2.3 重写 `frontend/src/pages/ReportPage.tsx`，调用 API + 渲染雷达图/分数条
- [x] 2.4 实现 AI 诊断卡片展示（severity 标签、estimated_hours、confidence 环）
- [x] 2.5 实现问题列表展示（issues 数组）
- [x] 2.6 实现 Badge Markdown 嵌入代码 + 一键复制按钮

## 3. HomePage 交互打磨

- [x] 3.1 重写 `frontend/src/pages/HomePage.tsx`，添加 GitHub URL 前端校验
- [x] 3.2 添加提交后 loading 动画（spinner/skeleton）
- [x] 3.3 添加错误 toast 提示

## 4. LeaderboardPage

- [x] 4.1 重写 `frontend/src/pages/LeaderboardPage.tsx`，调用 GET /api/leaderboard
- [x] 4.2 实现排行列表 UI（排名、仓库名、分数、badge 等级）
- [x] 4.3 前三名特殊视觉效果（金银铜）

## 5. 暗色主题 + 动画

- [x] 5.1 重写 `frontend/src/index.css`，暗色主题 CSS 变量
- [x] 5.2 添加卡片 hover 动画、页面进入 fadeIn 动画
- [x] 5.3 添加响应式适配（< 768px 移动端）

## 6. 测试与验证

- [x] 6.1 编写 leaderboard API 测试
- [x] 6.2 运行前端服务器验证暗色主题和动画效果
- [x] 6.3 运行 `pytest` + `npm test` 确认全部通过
