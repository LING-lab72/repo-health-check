## Why

分析超时、状态时序 bug 和重复代码是当前项目的三个核心问题。超大仓库（数千文件）导致分析器无限扫描超时；React 的 RESET 和 START_ANALYSIS 分在两个 useEffect 中触发同帧竞态，切换仓库时新分析被旧状态阻击；cache 和路由中散落不一致的 URL 规范化（有的缺 `.git` 处理），且 `analyze_local` 绕过公共 API 直接访问私有属性。这次修改统一解决这三类问题。

## What Changes

- 5 个 analyzer 文件添加 `MAX_FILES = 200` 文件扫描上限，防止超大仓库超时
- 合并 ReportPage 的 reset 和 analysis 两个 useEffect 为一个，消除 React 状态时序 bug
- `AnalysisCache` 新增 `normalize_url()` 统一规范化（去空格→去尾部`/`→去`.git`）
- `AnalysisCache` 新增 `invalidate()` 公共方法替代直接访问 `_lock`/`_cache`
- `get_by_hash()` 新增可选 `repo_url` 参数，支持精确查找消除哈希碰撞风险
- 全项目统一 `strip().rstrip("/")` → `cache.normalize_url()`
- `/api/analyze/status` 支持 `repo_url` 查询参数做精确缓存匹配

## Capabilities

### New Capabilities

无新增能力——本次修改均为现有能力的内部强化。

### Modified Capabilities

- `result-cache`: URL 规范化、`invalidate()` 公共方法、`get_by_hash()` 精确匹配增强
- `analyze-api`: 全路由统一 `cache.normalize_url()`，status 端点支持 `repo_url` 精确查询
- `analysis-aggregator`: 5 个 analyzer 增加 `MAX_FILES=200` 文件扫描上限
- `frontend-real-api`: ReportPage 合并两个 useEffect 消除状态竞态

## Impact

- **Backend**: `cache.py`, `analyze.py`, `vote.py`, `compare.py`, 5 个 `analyzer/*/analyzer.py`
- **Frontend**: `ReportPage.tsx`（删除 `useRef`、合并 effect）
- **API**: 无 breaking change，status 端点向后兼容（`repo_url` 为可选参数）
- **数据**: 缓存 key 规范化，旧缓存条目在 TTL 过期后自然淘汰
