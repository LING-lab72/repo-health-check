# 需求追踪矩阵

## 1. 功能需求追踪

| 需求 ID | 需求 | 设计/模块 | 实现位置 | 测试/验收 |
| --- | --- | --- | --- | --- |
| FR-01 | 仓库分析 | 分析流程、异步任务 | `backend/routes/analyze.py`, `backend/analyzer/` | `backend/tests/test_api.py`, E2E |
| FR-02 | 六维评分 | 六维分析器 | `backend/analyzer/*` | `backend/tests/test_aggregator.py` |
| FR-03 | 报告展示 | ReportPage | `frontend/src/pages/ReportPage.tsx` | 前端 build、人工验收 |
| FR-04 | AI 诊断 | ai/diagnose | `backend/ai/diagnose.py` | `backend/tests/test_ai_diagnose.py` |
| FR-05 | 缓存感知 | Cache service | `backend/services/cache.py` | `backend/tests/test_cache.py` |
| FR-06 | 导出分享 | export/reportAssets | `backend/routes/export.py`, `frontend/src/utils/reportAssets.ts` | `backend/tests/test_export.py` |
| FR-07 | 仓库对比 | ComparePage/compare route | `backend/routes/compare.py`, `frontend/src/pages/ComparePage.tsx` | 人工验收、build |
| FR-08 | 排行榜投票 | leaderboard/vote | `backend/routes/leaderboard.py`, `backend/routes/vote.py` | `backend/tests/test_leaderboard.py` |
| FR-09 | 用户认证 | OAuth/session | `backend/routes/auth.py`, `backend/services/session.py` | 手工登录测试 |
| FR-10 | 工程文档 | docs/OpenSpec | `docs/`, `openspec/` | 文档审查 |

## 2. 非功能需求追踪

| 非功能需求 | 实现策略 | 验证方式 |
| --- | --- | --- |
| 性能 | 缓存、异步任务、Compare 并行 | E2E、人工计时 |
| 安全 | XSS 转义、Session 强密钥、CORS、OAuth state | 安全测试用例 |
| 可用性 | 进度条、错误提示、一键启动 | 人工验收 |
| 可维护性 | 模块化目录、OpenSpec、软件工程文档 | 代码审查 |
| 可测试性 | pytest、Vitest、CI | 自动化测试 |
| 可扩展性 | 分析器分层、API 分层、SQLite | 架构审查 |

## 3. OpenSpec Capability 映射

| Capability | 覆盖需求 |
| --- | --- |
| cap-01 project-init | FR-10 |
| cap-02 analysis-engine | FR-01, FR-02 |
| cap-03 api-report | FR-01, FR-03, FR-06 |
| cap-04 ai-diagnosis | FR-04 |
| cap-05 frontend-polish | FR-03 |
| cap-06 deploy-e2e | FR-10 |
| cap-07 polish-final | FR-07, FR-08 |
| cap-08 async-optimize | FR-01, NFR 性能 |
| cap-14 proxy-auto-degrade | NFR 可靠性 |
| cap-16 react-bits-visual-redesign | FR-03, NFR 可用性 |
| cap-18 xss-security-fix | NFR 安全 |
| cap-19 security-architecture-hardening | NFR 安全、可维护性 |
| cap-20 report-leaderboard-ux | FR-03, FR-04, FR-06, FR-08 |

