## 1. Repo Clone Service — 代理支持与自动降级

- [x] 1.1 `clone.py` 新增 `_get_proxy()` 从环境变量和 .env 读取代理 URL
- [x] 1.2 `clone.py` 新增 `_test_github_direct()` 用 `git -c http.proxy="" ls-remote` 探测直连
- [x] 1.3 `clone.py` 新增 `_is_proxy_reachable()` 用 socket 检测代理端口是否在监听
- [x] 1.4 `clone.py` 新增 `_run_clone()` 抽取 clone 执行逻辑，通过 `-c` flag 传递代理
- [x] 1.5 `clone.py` 改造 `clone_repo()` 为自动降级策略（直连→代理→友好提示）
- [x] 1.6 `clone.py` 无代理时显式 `-c http.proxy=""` 清除全局代理配置
- [x] 1.7 `.env` 新增 `GIT_HTTP_PROXY=http://127.0.0.1:7890`

## 2. Analyze API — 错误缓存不再阻塞重新检测

- [x] 2.1 `analyze.py` `/api/analyze` 缓存命中错误结果时调用 `cache.invalidate()` 清除
- [x] 2.2 `analyze.py` 清除后继续执行实际检测（不再直接返回错误）
- [x] 2.3 验证 `/api/analyze/local` 已有类似处理（无需改动）

## 3. 运维配置

- [x] 3.1 启动命令传入代理环境变量：`GIT_HTTP_PROXY=... http_proxy=... https_proxy=... uvicorn ...`
- [x] 3.2 清除全局 `git config --global http.proxy/https.proxy`（避免干扰直连探测）
