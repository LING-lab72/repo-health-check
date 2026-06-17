## Context

cap-01/02 完成后，6 个分析器已工作、评分引擎已就绪，但端到端分析流程缺失。当前 `/api/analyze` 为 mock 桩，需要串联 git clone → 6 维分析 → 聚合评分 → 结果缓存 → API 响应 → Badge 生成的完整链路。

## Goals / Non-Goals

**Goals:**
- 实现 GitHub shallow clone 服务（--depth 1, 60s 超时）
- 实现 6 维分析聚合器，按 health-spec.yaml 权重计算健康总分
- 重写 POST /api/analyze 为真实分析端点
- 实现 shields.io 风格 SVG Badge 端点
- 实现内存缓存（30min TTL）避免重复分析

**Non-Goals:**
- 不实现异步任务队列（Celery/RQ），先同步 + GET status 伪异步
- 不持久化缓存（Redis），当前阶段内存足够
- 不支持私有仓库 clone（需后续 GitHub Token 集成）

## Decisions

### 1. Clone：subprocess git 而非 GitPython

**选择**：`subprocess.run(["git", "clone", "--depth", "1", url, tmpdir])`，60s timeout。

**理由**：GitPython 需要编译依赖，安装复杂。subprocess + 系统 git 更轻量。--depth 1 减少网络和磁盘开销。临时目录用 `tempfile.TemporaryDirectory` 自动清理。

**备选**：GitPython → 依赖重，安装问题多。直接 HTTP 下载 zip → 不含 .git 历史，无法用 radon/lizard 正确分析。

### 2. Aggregator：串行调用 6 个 Analyzer

**选择**：`for analyzer in analyzers: result = analyzer.analyze(repo_path)` 串行执行，读取 health-spec.yaml 的 dimensions weights 计算加权总分。

**理由**：6 个分析器间无数据依赖，串行更易调试和错误隔离。分析器本身不涉及 I/O（除 bandit/pip-audit 的 subprocess），串行不会显著增加延迟。

**备选**：asyncio 并行 → 复杂度增加，当前分析耗时主要由 git clone（网络）决定，并行收益有限。

### 3. API：同步分析 + 伪异步任务查询

**选择**：POST /api/analyze 同步等待完整分析结果返回（带 cache 时通常 < 5s）。GET /api/analyze/status?task_id=xxx 返回任务状态，task_id 为 repo_url 的 hash。

**理由**：分析耗时可控（shallow clone + 6 个轻量分析），同步返回更简单。task_id 机制预留未来真异步扩展。

### 4. Badge：内存生成 SVG，不依赖 shields.io

**选择**：内嵌 SVG 模板，按 health_score 映射 Badge 等级和颜色。URL 格式 `/api/badge/{repo_hash}`。颜色使用 shields.io 标准色值：brightgreen/yellow/orange/red。

**理由**：无需外部依赖，响应更快。SVG 模板极简（~500 bytes），按 health-spec.yaml 的 badge_levels 动态着色。

**备选**：跳转 shields.io endpoint → 依赖外部服务，网络延迟不可控。

### 5. Cache：TTL dict + 简单 LRU

**选择**：纯 Python dict，key=repo_url，value=(result, expire_time)。写入时记录 `time.time() + 1800`，读取时检查过期。最多保留 100 个条目，超出时清理所有过期项。

**理由**：无外部依赖，内存占用可控（每个 result < 10KB）。30 分钟 TTL 与 GitHub API 速率限制节奏匹配。

**备选**：Redis → 过度工程化。cachetools.TTLCache → 多一个依赖，收益有限。

## Risks / Trade-offs

- **[git clone 失败]** 网络问题或无效 URL → try/except 捕获，返回 400 错误
- **[大型仓库 OOM]** clone 后文件过多 → 单仓库限制 100 文件已在 code_quality 中实现；clone 层面设置 60s 超时
- **[并发写入 cache 不安全]** 多请求同时分析同一仓库 → 内置锁 `threading.Lock` 保护 cache 写操作
- **[API Breaking]** POST body 格式变更 → 文档标注，cap-03 为首次上线不影响已有用户
