# Frontend Real API

## Purpose

前端接入真实后端 API，展示分析结果：ECharts 雷达图、六维分数条、AI 诊断建议、问题列表、Badge 嵌入代码。首页 Hero 区域使用 CurvedLoop 弧形滚动标题动画。

## Requirements

### Requirement: 分析报告展示

系统 SHALL 在 ReportPage 中，当 `repoUrl` 或 `isLocal` 发生变化时，在同一 useEffect 中先执行 `dispatch({ type: 'RESET' })` 清除旧结果，再执行 `dispatch({ type: 'START_ANALYSIS' })` 触发新分析，最后调用 POST /api/analyze（sync 模式，skip_ai=true）获取分析结果并展示 ECharts 雷达图、六维分数条、问题列表。

#### Scenario: 切换仓库重新分析
- **WHEN** 用户从仓库 A 的报告页切换到仓库 B
- **THEN** RESET 清除仓库 A 的结果 → START_ANALYSIS 触发新请求 → 展示仓库 B 的 loading → 请求完成后渲染仓库 B 的报告

#### Scenario: 同仓库重复访问
- **WHEN** 用户在同一仓库的报告页刷新页面
- **THEN** useEffect 因 `repoUrl` 不变而触发 RESET + 新分析请求（无旧状态阻击）

### Requirement: AI 诊断展示

系统 SHALL 在报告页展示 ai_diagnosis 数组，每条建议显示 severity 标签和 confidence。

#### Scenario: 建议卡片

- **WHEN** ai_diagnosis 包含 3 条建议
- **THEN** 渲染 3 张卡片，severity 为 high 显示红色、medium 黄色、low 蓝色

### Requirement: Badge 嵌入代码

系统 SHALL 在报告页底部展示 Markdown 嵌入代码，支持一键复制。

### Requirement: HomePage CurvedLoop 标题

系统 SHALL 在 HomePage Hero 区域使用 CurvedLoop 组件渲染首页标题，文字内容 "Repo ✦ Health ✦ Check ✦"，沿 SVG 贝塞尔曲线弧形滚动，支持拖拽交互改变滚动方向和速度。

#### Scenario: 标题弧形滚动动画
- **WHEN** 用户访问首页
- **THEN** 标题区域显示沿曲线（curveAmount=280）循环的 "Repo ✦ Health ✦ Check ✦" 文字动画

#### Scenario: 拖拽改变滚动方向
- **WHEN** 用户在标题区域拖拽
- **THEN** 文字滚动方向随拖拽方向改变，拖拽结束后保持新的滚动方向

#### Scenario: 响应式字体
- **WHEN** 视口宽度 < 768px
- **THEN** CurvedLoop 字体缩小为 2.4rem；视口 < 480px 时缩小为 1.8rem
