## 1. 工程工具链配置

- [x] 1.1 创建 `.pre-commit-config.yaml`，集成 black + flake8（Python）和 ESLint + Prettier（TypeScript）
- [x] 1.2 创建 `backend/.flake8` 配置文件，设定最大行长度 100
- [x] 1.3 创建 `backend/pyproject.toml`，配置 black 格式化参数
- [x] 1.4 创建 `frontend/.eslintrc.cjs` 和 `frontend/.prettierrc` 配置文件
- [x] 1.5 创建根目录 `.gitignore`，排除 `node_modules/`、`__pycache__/`、`.venv/`、`dist/` 等

## 2. SDD 评分配置

- [x] 2.1 创建 `sdd/health-spec.yaml`，定义六个维度（code_quality、test_coverage、architecture、documentation、dependency_security、engineering）的 name、weight、thresholds、formula
- [x] 2.2 定义整体健康分计算公式和 Badge 等级映射（A/B/C/D 四级）
- [x] 2.3 验证 YAML 权重总和为 1.0，每个维度有至少一个子指标

## 3. 后端 FastAPI 骨架

- [x] 3.1 创建 `backend/requirements.txt`，声明 fastapi、uvicorn、radon、bandit、pip-audit、lizard、pyyaml
- [x] 3.2 创建 `backend/main.py`，初始化 FastAPI 应用，配置 CORS 中间件和 `/health` 端点
- [x] 3.3 创建 `backend/analyzer/__init__.py` 和 `backend/analyzer/base.py`，定义 `BaseAnalyzer` 抽象基类和 `AnalysisResult` 数据类
- [x] 3.4 创建六个分析维度子包：`backend/analyzer/code_quality/`、`test_coverage/`、`architecture/`、`documentation/`、`dependency_security/`、`engineering/`，每个含 `__init__.py` 和 `analyzer.py`（含空 `analyze()` 方法桩）
- [x] 3.5 创建 `backend/models/` 包，定义统一 JSON 响应模型（`ApiResponse`，含 code/message/data 字段）
- [x] 3.6 创建 `backend/routes/` 包和 `/api/analyze` 路由桩（返回 mock 统一响应格式）

## 4. 前端 React 骨架

- [x] 4.1 使用 Vite 模板创建 `frontend/` 项目（`npm create vite@latest frontend -- --template react-ts`）
- [x] 4.2 安装依赖：react-router-dom、echarts、echarts-for-react
- [x] 4.3 创建 `frontend/src/pages/` 目录，实现三个页面组件：`HomePage`（输入页）、`ReportPage`（报告页）、`LeaderboardPage`（排行榜页），初始均为占位内容
- [x] 4.4 配置 React Router 三页面路由（`/`、`/report/:repoId`、`/leaderboard`）
- [x] 4.5 创建 `frontend/src/context/AppContext.tsx`，使用 Context + useReducer 管理分析状态（idle/loading/success/error）
- [x] 4.6 在 ReportPage 集成 ECharts 雷达图组件，接收六维度评分 mock 数据渲染

## 5. 测试框架初始化

- [x] 5.1 创建 `backend/tests/` 目录和 `pytest.ini` 配置
- [x] 5.2 编写 BaseAnalyzer 接口契约测试（验证所有子类实现 analyze 方法）
- [x] 5.3 创建 `frontend/vitest.config.ts` 和 `frontend/src/__tests__/` 目录
- [x] 5.4 编写 AppContext 状态流转测试（idle → loading → success/error）

## 6. Harness CI 配置

- [x] 6.1 创建 `harness/` 目录和 CI 管道配置基础文件
- [x] 6.2 创建 Harness CI Pipeline YAML，包含 lint/test/build 三个阶段

## 7. 依赖安装与验证

- [x] 7.1 安装后端 Python 依赖 `pip install -r backend/requirements.txt`
- [x] 7.2 安装前端依赖 `cd frontend && npm install`
- [x] 7.3 验证后端启动 `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
- [x] 7.4 验证前端启动 `cd frontend && npm run dev`
