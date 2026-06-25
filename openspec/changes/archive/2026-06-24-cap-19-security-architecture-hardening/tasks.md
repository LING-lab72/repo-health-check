## 1. P0 安全修复

- [x] 1.1 Badge SVG 动态文本使用 HTML 转义
- [x] 1.2 Export HTML 动态文本使用 HTML 转义
- [x] 1.3 Export HTML 中 score/confidence/hours 等动态数字做范围限制
- [x] 1.4 导出文件名使用安全字符白名单
- [x] 1.5 Session 未设置 `SESSION_SECRET` 时拒绝启动
- [x] 1.6 GitHub OAuth 增加 state Cookie 校验
- [x] 1.7 `_pending_tasks` 使用锁保护
- [x] 1.8 投票默认不信任客户端 `X-Forwarded-For`

## 2. P1 架构与可靠性

- [x] 2.1 存储层从 JSON 文件迁移到 SQLite
- [x] 2.2 保留旧 storage 函数接口，降低路由改动范围
- [x] 2.3 支持旧 history/votes JSON 空库导入
- [x] 2.4 Compare 路由改为并行 clone/analyze
- [x] 2.5 Compare 路由异常时保证临时目录清理
- [x] 2.6 Analyze async 模式改为 `asyncio.create_task()`
- [x] 2.7 阻塞 clone 使用 `asyncio.to_thread()` offload
- [x] 2.8 修复 git `-c` 参数顺序，确保代理覆盖生效
- [x] 2.9 新增 GitHub Actions CI
- [x] 2.10 CI 覆盖 backend lint/test/E2E 和 frontend lint/test/build

## 3. P2 工程化与前端完善

- [x] 3.1 缓存读写使用深拷贝，避免嵌套对象污染
- [x] 3.2 Badge 颜色映射抽取为共享常量
- [x] 3.3 默认 `npx --no-install`，显式配置才允许在线安装
- [x] 3.4 新增 React ErrorBoundary
- [x] 3.5 补充 Iridescence、Dock、HomePage 输入、RadarChart、ScoreBar、GlassCard 的 a11y
- [x] 3.6 支持 `prefers-reduced-motion` 下禁用 WebGL 背景动画
- [x] 3.7 新增前端组件测试
- [x] 3.8 新增 XSS、缓存、AI Key、clone 命令顺序等后端回归测试
- [x] 3.9 删除 `backend/services/clone.py.bak`
- [x] 3.10 新增 CONTRIBUTING、SECURITY、CHANGELOG
- [x] 3.11 同步 `.env.example`、README、README_EN
- [x] 3.12 `.gitignore` 忽略 SQLite 运行时文件

## 4. OpenSpec 同步

- [x] 4.1 新增 `persistent-storage` 主规格
- [x] 4.2 新增 `security-hardening` 主规格
- [x] 4.3 更新 `analyze-api` 主规格
- [x] 4.4 更新 `ai-diagnosis` 主规格
- [x] 4.5 更新 `badge-api` 主规格
- [x] 4.6 更新 `frontend-real-api` 主规格
- [x] 4.7 更新 `leaderboard-api` 主规格
- [x] 4.8 更新 `repo-clone-service` 主规格
- [x] 4.9 更新 `result-cache` 主规格
- [x] 4.10 创建 cap-19 归档记录和 specs 快照

## 5. 验证

- [x] 5.1 前端 lint 通过
- [x] 5.2 前端 Vitest 通过
- [x] 5.3 前端生产构建通过
- [x] 5.4 后端源码语法检查通过
- [x] 5.5 SQLite storage smoke test 通过
- [x] 5.6 后端完整 pytest 由 CI 安装依赖后执行
