## 1. 仓库克隆服务

- [x] 1.1 创建 `backend/services/__init__.py`
- [x] 1.2 创建 `backend/services/clone.py`，实现 `clone_repo(url: str) -> Path`
- [x] 1.3 实现 git clone --depth 1 + 60s 超时 + TemporaryDirectory
- [x] 1.4 实现 URL 校验（必须以 github.com 开头）
- [x] 1.5 处理 clone 失败/超时/无效 URL 异常

## 2. 结果缓存服务

- [x] 2.1 创建 `backend/services/cache.py`，实现 `AnalysisCache` 类
- [x] 2.2 实现 `get(repo_url) -> dict | None` 带 TTL 过期检查
- [x] 2.3 实现 `set(repo_url, result)` 带 threading.Lock 线程安全
- [x] 2.4 实现容量控制：最大 100 条，满载时清理过期条目
- [x] 2.5 实现 `repo_url -> hash` 方法用于 badge URL

## 3. 分析聚合器

- [x] 3.1 创建 `backend/analyzer/aggregator.py`
- [x] 3.2 实现 `aggregate(repo_path, repo_url) -> dict` 串行调用 6 个 Analyzer
- [x] 3.3 读取 health-spec.yaml dimensions weights 计算加权总分
- [x] 3.4 按 badge_levels 映射 health_score → badge_level/badge_color
- [x] 3.5 单个分析器失败时降级处理（score=0 + error in issues）
- [x] 3.6 返回统一格式：{repo_url, health_score, badge_level, badge_color, dimensions[], analyzed_at}

## 4. 重写分析 API

- [x] 4.1 重写 `backend/routes/analyze.py` POST /api/analyze
- [x] 4.2 实现请求体校验：repo_url 字段存在且为合法 GitHub URL
- [x] 4.3 实现完整流程：cache check → clone → aggregate → cache save → response
- [x] 4.4 实现 GET /api/analyze/status?task_id=xxx 查询异步状态
- [x] 4.5 错误处理：400（无效 URL）/ 400（克隆失败）/ 500（分析异常）

## 5. Badge SVG 端点

- [x] 5.1 创建 `backend/routes/badge.py`
- [x] 5.2 实现 GET /api/badge/{repo_hash} 端点
- [x] 5.3 实现 SVG 模板生成，shields.io 风格（左侧 health / 右侧等级）
- [x] 5.4 颜色映射：A=brightgreen(#4c1) B=yellow(#dfb317) C=orange(#fe7d37) D=red(#e05d44)
- [x] 5.5 未缓存时返回 unknown(lightgrey) SVG
- [x] 5.6 设置 Content-Type: image/svg+xml

## 6. 注册路由与集成

- [x] 6.1 在 `backend/routes/__init__.py` 中注册 analyze + badge 路由
- [x] 6.2 验证 POST /api/analyze 端到端流程
- [x] 6.3 验证 GET /api/badge/{hash} 返回 SVG
- [x] 6.4 验证缓存命中/过期逻辑

## 7. 测试

- [x] 7.1 编写 `backend/tests/test_clone.py` clone 服务测试
- [x] 7.2 编写 `backend/tests/test_cache.py` 缓存服务测试
- [x] 7.3 编写 `backend/tests/test_aggregator.py` 聚合器测试
- [x] 7.4 编写 `backend/tests/test_api.py` API 端点集成测试
- [x] 7.5 编写 `backend/tests/test_badge.py` Badge SVG 生成测试
- [x] 7.6 运行 `pytest` 确认所有测试通过
