# Frontend Real API

## Purpose

前端接入真实后端 API，展示分析结果：ECharts 雷达图、六维分数条、AI 诊断建议、问题列表、Badge 嵌入代码。

## Requirements

### Requirement: 分析报告展示

系统 SHALL 在 ReportPage 中，当 `repoUrl` 或 `isLocal` 发生变化时，在同一 useEffect 中先执行 `dispatch({ type: 'RESET' })` 清除旧结果，再执行 `dispatch({ type: 'START_ANALYSIS' })` 触发新分析，最后调用 POST /api/analyze（sync 模式）获取分析结果并展示 ECharts 雷达图、六维分数条、问题列表。

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

#### Scenario: 浏览器 API Key 启用 AI
- **WHEN** 用户在首页配置 DeepSeek API Key
- **THEN** ReportPage SHALL 在 POST /api/analyze 请求中传递 `ai_api_key`，并设置 `skip_ai=false`

#### Scenario: 无 API Key 跳过 AI
- **WHEN** 用户未配置浏览器 API Key
- **THEN** 首次分析 SHALL 设置 `skip_ai=true`，用户可后续手动触发 AI 诊断

### Requirement: Badge 嵌入代码

系统 SHALL 在报告页底部展示包含后端 API base URL 的 Markdown 嵌入代码，支持一键复制。

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

### Requirement: HomePage 交互

系统 SHALL 在 HomePage 实现 URL 格式前端校验、loading 动画、错误 toast。

### Requirement: 前端错误边界

系统 SHALL 在 App 根组件中包裹 ErrorBoundary，组件渲染异常时展示友好的降级 UI，而不是整页白屏。

#### Scenario: 页面渲染异常
- **WHEN** 任一路由组件渲染时抛出异常
- **THEN** ErrorBoundary 展示错误提示和返回首页按钮

### Requirement: 无障碍基础支持

系统 SHALL 为主要交互控件和纯装饰元素提供基础无障碍语义。

#### Scenario: 装饰背景隐藏
- **WHEN** Iridescence WebGL 背景渲染
- **THEN** 背景容器 SHALL 设置 `aria-hidden="true"`

#### Scenario: 表单输入标签
- **WHEN** HomePage 渲染仓库 URL 输入框
- **THEN** 输入框 SHALL 提供 `aria-label`

#### Scenario: 分数条语义
- **WHEN** ScoreBar 渲染分数
- **THEN** 分数条 SHALL 使用 `role="progressbar"` 并提供 aria-valuemin/aria-valuemax/aria-valuenow

#### Scenario: 减少动画偏好
- **WHEN** 用户系统设置 `prefers-reduced-motion: reduce`
- **THEN** App SHALL 不挂载 Iridescence WebGL 背景动画

### Requirement: Cache-Aware Report UX

ReportPage SHALL request analysis in async mode, render cached results immediately, and poll task status for uncached analyses.

#### Scenario: Staged progress
- **WHEN** a report analysis is pending
- **THEN** ReportPage SHALL display staged progress for cache check, clone, code analysis, AI diagnosis, and report generation

#### Scenario: Automatic AI diagnosis
- **WHEN** ReportPage starts analysis
- **THEN** it SHALL send `skip_ai=false` and include browser-stored `ai_api_key` when available

#### Scenario: Compare shortcut
- **WHEN** a report is displayed
- **THEN** the page SHALL provide a shortcut to ComparePage with the current repository URL prefilled as `repo_a`

#### Scenario: Live badge preview
- **WHEN** a report is displayed
- **THEN** the badge embed section SHALL show a live color preview derived from `badge_color` and `health_score`

### Requirement: Reference Trend Chart

HistoryChart SHALL render when at least one history record exists and SHALL include a reference line for comparable repositories.

#### Scenario: Single history point
- **WHEN** a repository has exactly one history entry
- **THEN** HistoryChart SHALL render the current score and a benchmark/reference line

### Requirement: Repository PK Arena

ComparePage SHALL present side-by-side repository comparison as a lightweight PK arena after both repositories are analyzed.

#### Scenario: PK battle result
- **WHEN** two comparison results are available
- **THEN** ComparePage SHALL show animated score/health bars, identify the higher-scoring repository as winner, and display the score gap

#### Scenario: PK share poster
- **WHEN** comparison results are available and the user clicks the PK poster action
- **THEN** the frontend SHALL render both repositories, scores, badges, winner, and brand label to a downloadable PNG canvas image
