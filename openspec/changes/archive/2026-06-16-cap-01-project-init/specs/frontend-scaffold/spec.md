## ADDED Requirements

### Requirement: Vite + React + TypeScript 项目骨架

系统 SHALL 在 `frontend/` 目录下使用 Vite 初始化 React 18 + TypeScript 项目，包含基础配置。

#### Scenario: 开发服务器启动

- **WHEN** 执行 `npm run dev`
- **THEN** Vite 开发服务器在 `http://localhost:5173` 启动，显示默认页面

#### Scenario: TypeScript 编译

- **WHEN** 执行 `npx tsc --noEmit`
- **THEN** 无类型错误，编译通过

### Requirement: 三页面路由

系统 SHALL 使用 React Router 实现三个页面路由：首页（`/`，输入 GitHub URL）、报告页（`/report/:repoId`，展示体检结果）、排行榜页（`/leaderboard`）。

#### Scenario: 页面导航

- **WHEN** 用户在首页输入仓库 URL 并提交
- **THEN** 页面跳转至 `/report/<encoded_url>`，展示加载状态

#### Scenario: 排行榜访问

- **WHEN** 用户导航至 `/leaderboard`
- **THEN** 页面展示仓库健康排行榜（初始为空列表状态）

### Requirement: Context 状态管理

系统 SHALL 使用 React Context + useReducer 管理全局应用状态，包括分析结果、加载状态、错误信息。

#### Scenario: 分析状态流转

- **WHEN** 用户提交分析请求
- **THEN** 状态从 `idle` → `loading` → `success`（含分析结果）或 `error`（含错误信息）

### Requirement: ECharts 集成

系统 SHALL 集成 ECharts 库，在报告页展示雷达图（六维度评分）。

#### Scenario: 雷达图渲染

- **WHEN** 报告页接收到六个维度的评分数据
- **THEN** 雷达图正确渲染，六个维度分别显示对应分数

### Requirement: 前端依赖声明

系统 SHALL 在 `frontend/package.json` 中声明 React 18、React Router、ECharts、TypeScript、Vite、Vitest 等依赖。

#### Scenario: 依赖安装

- **WHEN** 执行 `npm install`
- **THEN** 所有依赖成功安装，`npm run dev` 正常启动
