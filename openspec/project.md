# Repo Health Check

## 项目概述
仓库健康体检工具：输入 GitHub 仓库 URL，自动分析代码质量、测试覆盖、
架构健康、文档完整、依赖安全、工程规范六个维度，生成体检报告、
雷达图和可嵌入 README 的健康 Badge。

## 技术栈
- 后端：Python 3.11+ / FastAPI / uvicorn
- 分析引擎：radon（圈复杂度）/ lizard（多语言）/ bandit（安全）/ pip-audit / npm audit
- 前端：React 18 / TypeScript / Vite / ECharts
- AI 诊断：OpenAI / DeepSeek API
- 存储：SQLite + 内存缓存
- 部署：Docker Compose / Vercel

## 编码规范
- Python：black 格式化 + flake8 检查
- TypeScript：ESLint + Prettier
- CI：GitHub Actions 执行后端 lint/test/E2E 与前端 lint/test/build
- 提交信息遵循 Conventional Commits

## 架构约定
- 后端：每个分析维度独立模块，统一 JSON 输出格式
- 前端：React + Context 状态管理，三页面（输入/报告/排行榜）
- SDD：所有评分规则由 sdd/health-spec.yaml 驱动

## 测试策略
- 后端：pytest 单元测试（每个分析模块）
- 前端：Vitest 组件测试
- 集成测试：本仓库自分析 smoke test

## Git 工作流
- main 分支保护
- 功能开发在 feature/ 分支，通过 PR 合并
- 每个 OpenSpec capability 对应一个 feature 分支

## 分析限制
- 单仓库最多分析 100 个源文件
- 支持语言：Python / JavaScript / TypeScript / Java / Go
