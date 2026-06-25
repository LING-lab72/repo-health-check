## Context

Repo Health Check 已具备完整 MVP 能力，但此前一些实现更偏本地演示：

- Session 默认密钥适合开发但不适合生产
- JSON 文件存储无法支撑多进程部署
- 前端可配置 DeepSeek Key，但 Key 没有真正进入后端 AI 调用链路
- Compare 与 async analyze 存在串行/伪异步和清理边界问题
- CI、文档、安全策略和前端错误降级不完整

本次设计目标是在不破坏现有 API 调用方式的前提下，提高公开部署安全性和工程可靠性。

## Goals / Non-Goals

**Goals:**

- 消除 P0 安全配置和输出注入风险
- 将排行榜/投票/历史数据迁移到 SQLite
- 保持现有路由和前端使用方式兼容
- 增加 CI 和关键回归测试
- 补齐 OpenSpec 主规格和归档快照

**Non-Goals:**

- 不引入 PostgreSQL、Redis 或 SQLAlchemy 等更重依赖
- 不实现新的分析维度（性能、社区活跃度、趋势预测等另行 capability）
- 不重构前端设计系统或替换 UI 框架
- 不一次性修复所有历史 flake8 E501 长行

## Decisions

### D1: Session Secret 未配置即失败

**决策**：`backend/services/session.py` 不再使用 `"dev-only-secret-change-in-production"` 默认密钥。缺少 `SESSION_SECRET` 时抛出 `RuntimeError`。

**理由**：签名 Cookie 的安全性完全依赖密钥。生产环境漏配时继续启动比显式失败更危险。

**Trade-off**：本地开发必须配置 `.env`；测试通过 `conftest.py` 设置测试密钥。

### D2: SQLite 替换 JSON 存储但保留函数接口

**决策**：`storage.py` 使用 SQLite 表 `history`、`votes`、`vote_cooldowns`，保留 `save_entry()`、`get_all()`、`get_history()`、`cast_vote()`、`get_by_url_hash()`。

**理由**：SQLite 零配置、标准库内置，适合本项目当前部署复杂度，同时比 JSON 文件更适合多进程读写。

**Trade-off**：仍不是分布式数据库，多实例跨机器部署需要 PostgreSQL 或托管数据库作为后续演进。

### D3: 旧 JSON 数据只在空库时导入

**决策**：SQLite history/votes 表为空时才尝试导入 `data/history.json` 和 `data/votes.json`。

**理由**：避免每次启动重复导入；保留从旧版本升级的平滑路径。

### D4: 请求级 AI Key 不持久化

**决策**：`ai_api_key` 作为 `/api/analyze` 可选字段，仅用于当次 AI 调用。缓存和 SQLite 中不保存该字段。

**理由**：用户浏览器 Key 可启用 AI 诊断，但服务端不应持久化用户密钥。

### D5: async analyze 使用 create_task + clone offload

**决策**：async 模式使用 `asyncio.create_task()` 创建后台任务，阻塞式 `clone_repo()` 用 `asyncio.to_thread()` offload。

**理由**：避免 background thread 中再 `asyncio.run()` 创建隔离事件循环，简化 async 语义。

### D6: Compare 并行但每个仓库独立清理

**决策**：Compare 使用 `asyncio.gather()` 并行分析两个仓库，每个 `analyze_one()` 在自己的 `finally` 中清理临时目录。

**理由**：缩短等待时间，并保证任一仓库失败时已克隆目录也能清理。

### D7: `npx --no-install` 作为安全默认值

**决策**：JS/TS 分析默认用 `npx --no-install`，仅 `ALLOW_NPX_INSTALL=1` 时允许 `--yes`。

**理由**：分析外部仓库时自动下载 npm 包会引入网络不确定性和供应链风险。

### D8: 前端错误边界和基础 a11y

**决策**：在 App 根组件包裹 ErrorBoundary，补充装饰背景 `aria-hidden`、输入 aria-label、progressbar 语义、键盘触发和 reduced-motion 降级。

**理由**：提升异常可恢复性和辅助技术体验，不改变核心 UI。

## Risks / Trade-offs

- **SQLite 单机边界**：适合单机/单容器部署，多机器部署仍需升级到外部数据库。
- **Session Secret 严格要求**：漏配会导致启动失败；但这是安全基线，README/.env.example/SECURITY 已补充。
- **npx 不自动安装**：未预装 eslint/madge 的环境会跳过部分 JS 分析信号；可通过镜像预装或显式 `ALLOW_NPX_INSTALL=1` 恢复旧行为。
- **请求级 API Key 经过后端**：Key 不持久化，但仍经过网络请求；生产部署应使用 HTTPS。
