## Why

本次修改来自一次全面项目体检后的修复清单，覆盖 P0 安全问题、P1 架构可靠性问题，以及一组可立即落地的 P2 工程化完善项。

核心风险包括：

- Session 使用硬编码默认密钥，生产环境漏配 `SESSION_SECRET` 时 Cookie 可被伪造
- SVG/HTML 导出存在动态内容注入风险，需要持续强化转义和数值白名单
- async 分析任务集合存在并发修改风险，且后台分析混用线程和 `asyncio.run()`
- JSON 文件存储不适合多进程/多实例部署，排行榜和投票数据一致性不足
- 前端缺少错误边界和部分基础 a11y 语义
- CI 缺失，修复无法通过 GitHub 标准工作流持续验证

## What Changes

- **安全加固**
  - `SESSION_SECRET` 未设置时拒绝启动
  - GitHub OAuth 增加 state Cookie 校验
  - Badge SVG 和 Export HTML 动态内容转义，导出报告数值 clamp
  - 投票默认不信任 `X-Forwarded-For`
  - `npx` 默认 `--no-install`，避免分析外部仓库时自动下载包

- **后端架构**
  - 存储层从 JSON 文件迁移到 SQLite，保留原 `storage.py` 函数接口
  - 支持旧 `history.json` / `votes.json` 一次性迁移
  - 缓存读写改为深拷贝，避免嵌套对象污染
  - Compare 路由并行 clone + analyze，并确保异常时清理临时目录
  - Analyze async 模式使用 `asyncio.create_task()`，clone 使用 thread offload
  - 修复 git `-c` 参数顺序，确保直连探测和 clone 代理覆盖真实生效

- **前端与测试**
  - 新增 ErrorBoundary
  - 补充 Iridescence、Dock、HomePage 输入、RadarChart、ScoreBar、GlassCard 的 a11y 支持
  - 增加组件测试、XSS 回归测试、缓存深拷贝测试、AI Key override 测试和 clone 命令顺序测试
  - 新增 GitHub Actions CI：backend lint/test/E2E + frontend lint/test/build

- **文档与仓库卫生**
  - 新增 `CONTRIBUTING.md`、`SECURITY.md`、`CHANGELOG.md`
  - 同步 `.env.example`、README/README_EN
  - 删除 `backend/services/clone.py.bak`
  - 忽略 SQLite 运行时数据库文件

## Capabilities

### New Capabilities

- `persistent-storage`：SQLite 持久化历史、投票和投票冷却
- `security-hardening`：安全基线，包括 session、OAuth state、导出转义、代理头和 npx 安全默认值

### Modified Capabilities

- `analyze-api`：请求级 AI Key、缓存补诊断、pending 任务去重、原生 async 后台分析
- `ai-diagnosis`：支持请求级 DeepSeek key
- `badge-api`：转义动态 SVG 文本并复用共享颜色常量
- `frontend-real-api`：ErrorBoundary、a11y、prefers-reduced-motion、AI Key 请求传递
- `leaderboard-api`：SQLite 排行榜和持久化投票
- `repo-clone-service`：修正 git `-c` 参数位置
- `result-cache`：嵌套结构深拷贝隔离

## Impact

- **Frontend**: 增加 ErrorBoundary/a11y 和组件测试，用户流程不破坏
- **Backend**: SQLite 替换 JSON 存储；Session 生产配置更严格
- **API**: 无 breaking change；`/api/analyze` 扩展可选 `ai_api_key`
- **Runtime**: 生产必须配置 `SESSION_SECRET`
- **Data**: 旧 JSON 数据可在 SQLite 空库时自动导入
