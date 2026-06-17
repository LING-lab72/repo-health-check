## Why

cap-01~06 完成了核心功能开发，但仍有大量细节需要打磨：TypeScript 类型同步、环境变量加载、持久化存储、对比模式、投票系统、JS/TS 深层分析、社区文档等。本变更规范化追踪所有后期优化。

## What Changes

- 修复 TypeScript 类型定义与后端响应对齐
- 添加 python-dotenv 环境变量加载
- Badge URL 改为相对路径
- 创建 Navbar 全局导航
- JSON 文件持久化存储（data/ 目录）
- 添加历史趋势图 + 对比模式 + 投票系统
- 增强 JS/TS 分析（ESLint / coverage / madge）
- 生成社区文档（README / 挑战赛 / Badge 画廊 / Issue & PR 模板）
- 添加 MIT LICENSE

## Capabilities

### New Capabilities
- `compare-mode`: 双仓库并排雷达图对比
- `vote-system`: 👍 投票 + 每周挑战
- `history-trend`: 历史分析趋势折线图
- `js-ts-deep-analyze`: ESLint + coverage 解析 + madge 循环依赖
- `community-docs`: 挑战赛规则 + Badge 画廊 + 模板

### Modified Capabilities
- `frontend-real-api`: AnalysisData 类型对齐、Navbar、Badge 相对路径
- `backend-main`: dotenv 加载
- `storage`: 追加式 JSON 持久化
- `leaderboard-api`: 投票集成

## Impact

- 新增：~10 个文件（Navbar/HistoryChart/ComparePage/vote/storage/js_utils/community/.github）
- 修改：~8 个文件（AppContext/ReportPage/main/storage/leaderboard/App/Navbar）
