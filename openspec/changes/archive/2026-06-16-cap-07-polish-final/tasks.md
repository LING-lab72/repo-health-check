## 1. TypeScript & 配置修复

- [x] 1.1 更新 AppContext.tsx AnalysisData 接口对齐后端响应
- [x] 1.2 删除 ReportPage.tsx 未使用的 BADGE_BASE 常量
- [x] 1.3 Badge URL 改为相对路径 `/api/badge/{hash}`
- [x] 1.4 backend/main.py 添加 load_dotenv() 加载 .env

## 2. 持久化存储

- [x] 2.1 重写 backend/services/storage.py 为追加式 JSON 存储
- [x] 2.2 分析完成后 save_entry() 写入 data/history.json
- [x] 2.3 Leaderboard API 改为读取持久化数据

## 3. 历史趋势

- [x] 3.1 创建 backend/routes/history.py + GET /api/history/{repo_url}
- [x] 3.2 创建 frontend/src/components/HistoryChart.tsx ECharts 折线图
- [x] 3.3 ReportPage 分析成功后自动加载历史趋势

## 4. 对比模式

- [x] 4.1 创建 backend/routes/compare.py + GET /api/compare
- [x] 4.2 创建 frontend/src/pages/ComparePage.tsx 双雷达图
- [x] 4.3 注册 /compare 路由 + Navbar 链接

## 5. 投票系统

- [x] 5.1 创建 backend/routes/vote.py + POST /api/vote
- [x] 5.2 storage.py 添加 cast_vote() + data/votes.json
- [x] 5.3 LeaderboardPage 每行添加 👍 按钮 + 本周最健康仓库

## 6. JS/TS 深层分析

- [x] 6.1 创建 backend/analyzer/js_utils.py（npx + coverage 解析）
- [x] 6.2 code_quality 集成 ESLint 检测
- [x] 6.3 test_coverage 解析 lcov/coverage-summary
- [x] 6.4 architecture 集成 madge 循环依赖检测

## 7. UI 组件

- [x] 7.1 创建 frontend/src/components/Navbar.tsx（首页/排行榜/对比/GitHub）
- [x] 7.2 在 App.tsx 中集成 Navbar
- [x] 7.3 更新 index.css 添加 Navbar 样式

## 8. 项目文档

- [x] 8.1 创建 MIT LICENSE
- [x] 8.2 完善 README.md（特性/快速开始/贡献/技术栈）
- [x] 8.3 创建 community/challenge.md 2周挑战赛
- [x] 8.4 创建 community/badge-gallery.md Badge 画廊
- [x] 8.5 创建 .github/ISSUE_TEMPLATE/* 3个模板
- [x] 8.6 创建 .github/PULL_REQUEST_TEMPLATE.md

## 9. 验证

- [x] 9.1 TypeScript 编译 0 错误
- [x] 9.2 npm run build 成功
- [x] 9.3 pytest 76/76 全部通过
