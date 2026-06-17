## Context

当前项目为空仓库，需要搭建完整的工程骨架。项目目标是对 GitHub 仓库进行六个维度的健康体检（代码质量、测试覆盖、架构健康、文档完整、依赖安全、工程规范），生成体检报告、雷达图和可嵌入 README 的健康 Badge。技术栈已确定：后端 Python 3.11+/FastAPI，前端 React 18/TypeScript/Vite。

## Goals / Non-Goals

**Goals:**
- 建立后端 FastAPI 项目结构，六大分析维度独立模块
- 建立前端 React + Vite 项目结构，三页面路由（输入/报告/排行榜）
- 配置代码格式化与检查工具链（black/flake8/ESLint/Prettier）
- 创建 SDD 健康评分配置文件 `sdd/health-spec.yaml`
- 初始化测试框架（pytest/vitest）

**Non-Goals:**
- 不实现具体分析逻辑（各维度分析属后续变更范围）
- 不配置部署（CI/CD、Vercel 部署属后续变更）
- 不接入 OpenAI/DeepSeek API（AI 诊断属后续变更）
- 不实现 GitHub API 对接

## Decisions

### 1. 项目结构：monorepo 而非多仓库

**选择**：单仓库 monorepo，`backend/`、`frontend/`、`sdd/` 三目录平级。

**理由**：项目规模适中，前后端紧密耦合（API 契约共享），monorepo 降低协作成本。后续可拆分为独立仓库。

**备选**：前后端分仓 → 增加 CI/CD 复杂度，当前阶段不必要。

### 2. 后端：FastAPI + 模块化分析器

**选择**：`backend/` 下每个分析维度一个子包（如 `backend/analyzers/code_quality/`），统一通过 `BaseAnalyzer` 抽象基类约束接口。

**理由**：FastAPI 原生 async 支持、自动 OpenAPI 文档生成；模块化设计便于独立开发和测试；统一接口（`analyze(repo_path) -> AnalysisResult`）保持可扩展性。

**备选**：Django + DRF → 过重，本项目只需轻量 API 层。Flask → 缺少 async 和一流的类型提示支持。

### 3. 前端：Vite + React Context（不引入 Redux）

**选择**：Vite 作为构建工具，React Context + useReducer 管理全局状态（分析结果、加载状态、错误处理）。

**理由**：应用状态简单（单表单输入 → 异步结果 → 展示），Context 足以胜任。ECharts 通过按需引入减少 bundle 体积。

**备选**：Redux/Zustand → 当前阶段过度工程化，状态复杂度不匹配。

### 4. 评分引擎：YAML 驱动

**选择**：评分规则集中在 `sdd/health-spec.yaml`，后端解析 YAML 后动态执行评分。

**理由**：SDD 核心理念——规则与代码分离，调整权重无需改代码。YAML 可读性好，非技术人员也能参与规则调优。

### 5. 代码规范：Pre-commit Hook

**选择**：通过 `pre-commit` 集成 black/flake8（Python）和 ESLint/Prettier（TypeScript），在提交前自动检查。

**理由**：强制规范一致性，避免 CI 阶段才发现格式问题。

## Risks / Trade-offs

- **[工具链版本漂移]** black/flake8/ESLint 升级可能引入新规则 → 使用 `pre-commit` 锁版本，Renovate 定期更新
- **[monorepo 耦合风险]** 前后端共享 `sdd/health-spec.yaml` 可能因 YAML 结构变更导致双方爆红 → 在 specs 中定义 YAML Schema 校验规则
- **[Vite 构建配置复杂度]** 后期可能需配置代理到 FastAPI 后端 → 设计阶段在 `vite.config.ts` 预留 proxy 配置段，当前指向 mock
