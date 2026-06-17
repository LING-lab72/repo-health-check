## Context

前端骨架已搭建（React Router 三页面 + AppContext），后端 API 已就绪（/api/analyze、/api/badge、ai_diagnosis）。需要对接真实 API 并美化 UI。

## Goals / Non-Goals

**Goals:**
- ReportPage 完整展示分析结果（雷达图、分数条、AI 诊断、问题列表）
- HomePage 交互打磨（loading、URL 校验、错误处理）
- LeaderboardPage 展示仓库排行
- 暗色主题 + 动画过渡
- Badge 嵌入代码展示

**Non-Goals:**
- 不实现用户登录系统
- 不实现历史分析记录持久化

## Decisions

### 1. ECharts 雷达图：直接用 echarts 库渲染

**选择**：在 ReportPage 中用 `echarts.init()` 原生 API 渲染雷达图，不使用 echarts-for-react 封装。

**理由**：更精确控制尺寸和动画，减少一层依赖。雷达图选项简单（6 轴 + 1 系列），原生 API 约 20 行。

### 2. 状态管理：复用 AppContext

**选择**：HomePage 点击分析 → dispatch START_ANALYSIS → fetch /api/analyze → dispatch SUCCESS/ERROR。ReportPage 读取 state.analysisResult。

**理由**：Context 已定义完整的 idle/loading/success/error 状态机，无需引入新状态库。

### 3. 暗色主题：CSS 变量

**选择**：在 `index.css` 中定义 `:root` CSS 变量（--bg, --text, --card, --accent），组件通过 `var(--xxx)` 引用。

**理由**：零 JavaScript 开销，浏览器原生支持。未来可扩展为亮色/暗色切换。

### 4. 排行榜后端：直接遍历缓存

**选择**：新增 GET /api/leaderboard，遍历 AnalysisCache 返回按 health_score 降序排列的结果列表。

**理由**：数据已存在缓存中，无需新存储。排行榜随缓存自然更新。

### 5. 动画：CSS transition + keyframes

**选择**：卡片 hover/enter 用 `transition`，页面首次加载用 `@keyframes fadeIn`。不引入 Framer Motion 等重依赖。

**理由**：轻量级动画满足需求，保持 bundle 体积小。

## Risks / Trade-offs

- **[缓存数据即排行榜]** 缓存过期后排行榜会缩水 → 可接受，后续可加持久化
- **[雷达图性能]** 6 轴雷达图渲染 < 10ms，无性能风险
- **[跨域]** Vite proxy 已配置，开发环境无问题
