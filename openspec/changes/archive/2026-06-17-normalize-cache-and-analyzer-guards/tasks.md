## 1. Result Cache — URL 规范化与封装

- [x] 1.1 `cache.py` 添加 `normalize_url()` 静态方法（strip → rstrip / → rstrip .git）
- [x] 1.2 `cache.py` 添加 `invalidate(repo_url)` 公共方法，替代直接访问 `_lock`/`_cache`
- [x] 1.3 `cache.py` `get_by_hash()` 新增可选 `repo_url` 参数，支持精确查找回退
- [x] 1.4 `analyze.py` `analyze_local()` 中 `cache._cache.pop()` → `cache.invalidate()`

## 2. Analyze API — 统一 normalize_url 调用

- [x] 2.1 `analyze.py` `analyze_repo()` 中 `strip().rstrip("/")` → `cache.normalize_url()`
- [x] 2.2 `analyze.py` `_run_analysis()` 内部 URL 规范化
- [x] 2.3 `analyze.py` `analyze_local()` 硬编码 URL 规范化
- [x] 2.4 `analyze.py` async 响应 `data` 中附带 `repo_url` 字段
- [x] 2.5 `analyze.py` `analyze_status()` 接受可选 `repo_url` 查询参数，传入 `get_by_hash` 精确匹配
- [x] 2.6 `vote.py` `strip().rstrip("/")` → `cache.normalize_url()`
- [x] 2.7 `compare.py` `strip().rstrip("/")` ×2 → `cache.normalize_url()`

## 3. Analyzer MAX_FILES 上限

- [x] 3.1 `architecture/analyzer.py` 添加 `MAX_FILES = 200`，替换硬编码 100
- [x] 3.2 `documentation/analyzer.py` 添加 `MAX_FILES = 200`，替换 `_score_comment_density` 中硬编码 100
- [x] 3.3 `dependency_security/analyzer.py` 添加 `MAX_FILES = 200`，限制 `_run_pip_audit` 中 `rglob`
- [x] 3.4 确认 `test_coverage/analyzer.py` 已有 MAX_FILES=200（无需改动）
- [x] 3.5 确认 `engineering/analyzer.py` 无文件扫描循环（无需改动）
- [x] 3.6 确认 `code_quality/analyzer.py` 已有 MAX_FILES=100（保持原有值）

## 4. Frontend — React 状态竞态修复

- [x] 4.1 `ReportPage.tsx` 合并 reset effect 和 analysis effect 为一个 useEffect
- [x] 4.2 删除 `if (state.status === 'success' || state.status === 'error') return` 阻击行
- [x] 4.3 删除 `fetchStartedRef` 引用和 `useRef` import
- [x] 4.4 验证路由切换时 `dispatch RESET` → `dispatch START_ANALYSIS` 在同一 effect 顺序执行
