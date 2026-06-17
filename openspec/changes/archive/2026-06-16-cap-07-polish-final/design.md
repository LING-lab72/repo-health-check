## Context

cap-06 完成后项目已可运行，但存在细节问题（TS 类型错配、硬编码 URL、数据丢失等）和功能缺口（对比、投票、历史、JS分析）。

## Goals / Non-Goals

**Goals:** TS 类型对齐、dotenv 加载、持久化存储、Navbar、历史趋势、对比模式、投票、JS/TS 分析、社区文档

**Non-Goals:** 不新增数据库、不重构架构

## Key Decisions

- **持久化**：单个 `data/history.json` 追加写入 + `data/votes.json` 独立管理
- **对比**：GET /api/compare 串行 clone 两个仓库
- **JS/TS**：npx 调用 ESLint/madge，解析 lcov/coverage-summary
- **投票**：POST /api/vote 递增计数，前端即时刷新

## Files Changed

| 类别 | 文件 | 操作 |
|------|------|------|
| 类型 | AppContext.tsx | 重写 AnalysisData 接口 |
| 配置 | main.py | 添加 load_dotenv() |
| 前端 | ReportPage.tsx | 删除 BADGE_BASE、添加 HistoryChart |
| 前端 | Navbar.tsx | 新建全局导航 |
| 前端 | ComparePage.tsx | 新建对比页 |
| 前端 | HistoryChart.tsx | 新建趋势图 |
| 后端 | storage.py | 重写为追加式 |
| 后端 | history.py | 新建 GET /api/history |
| 后端 | compare.py | 新建 GET /api/compare |
| 后端 | vote.py | 新建 POST /api/vote |
| 后端 | js_utils.py | 新建 JS/TS 工具 |
| 社区 | README.md 等 7 个文件 | 新建文档 |
| 项目 | LICENSE | 新建 MIT |
