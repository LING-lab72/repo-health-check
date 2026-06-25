# 风险与质量保证计划

## 1. 质量目标

| 目标 | 度量 |
| --- | --- |
| 功能正确 | 核心流程可运行，主要测试通过 |
| 前端稳定 | 首页、报告、对比、排行榜、About 不回退 |
| 安全可靠 | XSS、Session、CORS、任务竞态有防护 |
| 易维护 | 模块清晰，文档完整，OpenSpec 可追踪 |
| 可发布 | 有 tag、release notes、CI/CD |

## 2. 风险清单

| 风险 | 概率 | 影响 | 应对 |
| --- | --- | --- | --- |
| UI 被后续功能覆盖破坏 | 中 | 高 | 使用 `v2.1.0` tag 锁定稳定版，功能按小块移植 |
| GitHub 克隆失败 | 高 | 中 | 代理配置、超时、错误提示 |
| 大仓库分析慢 | 中 | 中 | 异步任务、进度条、缓存 |
| LLM API 不可用 | 中 | 低 | 本地规则诊断降级 |
| XSS 注入 | 低 | 高 | HTML/SVG 转义 |
| 多进程数据不一致 | 中 | 中 | SQLite 替代 JSON 文件 |
| CI 配置不兼容平台 | 中 | 中 | GitHub Actions 与 GitLink 分别维护 |

## 3. 质量保证活动

### 3.1 代码审查

重点审查：
- 用户输入。
- HTML/SVG 输出。
- 文件系统操作。
- 临时目录清理。
- 缓存和异步任务并发。

### 3.2 自动化测试

- 后端 pytest。
- 前端 Vitest。
- 前端 lint/build。
- E2E 自测脚本。

### 3.3 回归测试

关键 UI 回归：
- 首页高级视觉。
- Report 页面导出和 AI 诊断。
- Compare 页面 A / VS / B 布局。
- About cap 数量。

## 4. 发布质量门禁

发布前必须完成：

```bash
python -m pytest backend/tests -q
cd frontend
npm run lint
npm test -- --run
npm run build
```

## 5. 回退策略

当前稳定版本：

```bash
git checkout v2.1.0
```

创建恢复分支：

```bash
git checkout -b restore-v2.1.0 v2.1.0
```

