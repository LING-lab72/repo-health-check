## Why

仓库健康体检工具需要先建立完整的技术骨架和工程规范，才能在稳定的基础之上推进六个维度的分析功能开发。当前项目为空仓库，需要初始化前后端项目结构、依赖管理和开发工具链。

## What Changes

- 初始化 Python/FastAPI 后端项目结构，建立六大分析维度模块骨架
- 初始化 React 18 + TypeScript + Vite 前端项目结构，规划三页面路由
- 配置包管理器与依赖声明文件（requirements.txt / package.json）
- 配置代码格式化工具（black / Prettier）和检查工具（flake8 / ESLint）
- 创建 SDD 驱动的健康评分配置文件 `sdd/health-spec.yaml`
- 建立 pytest / vitest 测试框架基础配置

## Capabilities

### New Capabilities
<!-- Capabilities being introduced. Replace <name> with kebab-case identifier (e.g., user-auth, data-export, api-rate-limiting). Each creates specs/<name>/spec.md -->
- `backend-scaffold`: FastAPI 后端骨架，含六个分析维度空模块、统一 JSON 输出格式、CORS 中间件、基础路由
- `frontend-scaffold`: React 18 + TypeScript + Vite 前端骨架，含输入页/报告页/排行榜页、Context 状态管理、ECharts 集成
- `sdd-config`: 健康评分规则配置文件 health-spec.yaml，定义六个维度的评分权重、阈值和计算公式

### Modified Capabilities
<!-- Existing capabilities whose REQUIREMENTS are changing (not just implementation).
     Only list here if spec-level behavior changes. Each needs a delta spec file.
     Use existing spec names from openspec/specs/. Leave empty if no requirement changes. -->
（无，项目初始化无现有能力）

## Impact

- 新增目录：`backend/`、`frontend/`、`sdd/`
- 开发工具链：black + flake8（Python）、ESLint + Prettier（TypeScript）
- 测试框架：pytest（后端）、vitest（前端）
- 无现有代码受影响
