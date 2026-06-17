## Context

当前代码库存在三类一致性问题：

1. **URL 规范化散落**：`strip().rstrip("/")` 出现在 vote.py、compare.py 等多个路由中，且都缺少 `.git` 后缀处理。`cache.normalize_url()` 已存在但未被全局使用。
2. **缓存封装泄露**：`analyze_local()` 直接访问 `cache._lock` 和 `cache._cache.pop()` 私有属性，违反封装原则。
3. **超大仓库无保护**：architecture、documentation、dependency_security 等 analyzer 的文件扫描循环无上限，数千文件仓库导致 180s 超时。
4. **React 状态竞态**：ReportPage 中 `dispatch RESET` 和 `state.status === 'success'` 检查分在两个 useEffect，同一渲染帧内 dispatch 后 state 未更新，切换仓库时旧状态阻击新分析。

所有修改已完成并通过 lint，此设计文档记录技术决策。

## Goals / Non-Goals

**Goals:**
- 全项目统一 URL 规范化入口：`cache.normalize_url()` 作为唯一实现
- 缓存对外暴露完整公共 API（get / set / invalidate / get_by_hash），消除私有属性访问
- 所有文件扫描循环有 `MAX_FILES` 上限，防止超大仓库超时
- 前端分析触发逻辑消除 React 状态竞态

**Non-Goals:**
- 不改变缓存 TTL 或容量策略
- 不改动克隆超时或分析超时配置
- 不新增 API 端点或 breaking change
- 不修改 analysis-aggregator 的并发模型（已改为 parallel）

## Decisions

### D1: `cache.normalize_url()` 作为唯一规范化入口

**决策**：在 `AnalysisCache` 上添加 `normalize_url()` 静态方法，实现三步处理：`strip()` → `rstrip("/")` → `rstrip(".git")`（大小写不敏感）。全项目所有路由中处理 repo_url 的地方统一调用此方法。

**替代方案考虑**：
- ❌ 保持各处 `strip().rstrip("/")` — 缺少 `.git` 处理，且散落维护成本高
- ❌ 单独创建 `normalize_url()` 工具函数 — 与缓存关系紧密，放在 `AnalysisCache` 上语义更清晰

### D2: `invalidate()` 替代私有属性访问

**决策**：在 `AnalysisCache` 上添加 `invalidate(repo_url)` 公共方法，封装 `self._cache.pop(repo_url, None)` + 锁保护。`analyze_local()` 中原本的 `with cache._lock: cache._cache.pop(repo_url, None)` 改为 `cache.invalidate(repo_url)`。

**替代方案考虑**：
- ❌ 保持私有属性访问 — 未来 `_cache` 改动（如换 Redis）会导致多处置换点
- ❌ 用 `set(repo_url, None)` 标记 — 与现有 `_error` 标记语义冲突

### D3: `MAX_FILES` 常量化

**决策**：参考 `code_quality/analyzer.py` 中的 `MAX_FILES = 100` 模式，在 architecture、documentation、dependency_security 三个 analyzer 中添加 `MAX_FILES = 200` 常量。选择 200 而非 100 是因为这几个分析器每文件开销较小（仅 AST 解析/注释统计/文件匹配）。code_quality 保持 100（radon 分析每文件开销大），test_coverage 已有 200。

**替代方案考虑**：
- ❌ 不加限制 — 超大仓库直接超时
- ❌ 统一 100 — 对轻量 analyzer 过于保守，采样不足会影响分析准确性

### D4: 合并 React useEffect

**决策**：将 ReportPage 中分离的 reset effect 和 analysis effect 合并为一个。`dispatch RESET` 和 `dispatch START_ANALYSIS` 在同一 effect 中顺序执行，消除跨 effect 的 state 时序问题。删除 `fetchStartedRef` 和 `state.status === 'success'` 阻击行。

**替代方案考虑**：
- ❌ 用 `useLayoutEffect` 做 RESET — 增加复杂度且仍有时序窗口
- ❌ 用 ref 跟踪 repoUrl 变化 — 引入新的状态管理概念，不合 idiomatic React

## Risks / Trade-offs

- **[哈希碰撞风险]** → `get_by_hash` 无 `repo_url` 时的 fallback 仍用 12 位 SHA-256 截断迭代。当前前端已改为 `force_sync: true`，不触发 async 轮询模式，碰撞风险降为零。未来恢复 async 模式时，前端可从 `data.repo_url` 回传给 status 端点做精确匹配。
- **[TTL 缓存 key 变更]** → `normalize_url` 规范化后，旧的未规范化 key（如带 `.git` 后缀）与新的规范化 key 不匹配。30 分钟 TTL 后旧缓存自然淘汰，无需迁移。
- **[MAX_FILES 采样偏差]** → 对超大仓库只扫描前 200 文件，可能漏过后面的质量问题。但 200 文件足够代表仓库整体质量趋势，且避免超时比绝对准确更优先。
