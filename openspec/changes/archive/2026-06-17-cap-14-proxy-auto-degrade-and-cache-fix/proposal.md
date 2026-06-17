## Why

项目在国内网络环境下无法正常使用：GFW 阻断 GitHub 连接导致 git clone 失败；即使配置了代理，Python subprocess 无法继承 `git config --global` 代理设置；更严重的是，第一次克隆失败后错误结果被内存缓存，后续即使网络恢复也无法重新检测——永远返回第一次的错误信息。

## What Changes

- `clone.py` 全面改造为自动降级策略：直连探测 → 代理回退 → 友好中文提示
- 新增 `_get_proxy()` 从环境变量和 .env 文件读取代理配置
- 新增 `_test_github_direct()` 用 `git -c http.proxy="" ls-remote` 绕过全局代理做真正的直连测试
- 新增 `_is_proxy_reachable()` 用 socket 检测代理端口是否在监听
- 新增 `_run_clone()` 抽取 clone 执行逻辑，通过 `-c` flag 传递代理而非全局配置
- `analyze.py` 修复错误缓存阻塞重新检测的问题：缓存命中错误结果时先 `invalidate` 再重新检测
- `.env` 新增 `GIT_HTTP_PROXY` 配置项

## Capabilities

### New Capabilities

无新增能力——本次修改均为现有能力的内部强化。

### Modified Capabilities

- `repo-clone-service`: 代理支持、自动降级（直连→代理→友好提示）、`-c` flag 传递代理
- `result-cache`: 错误结果不再永久阻塞（通过 `invalidate` 语义由调用方控制）
- `analyze-api`: `/api/analyze` 端点遇到错误缓存时自动清除并重新检测

## Impact

- **Backend**: `clone.py`（重大改造）, `analyze.py`（缓存错误处理修复）
- **Config**: `.env` 新增 `GIT_HTTP_PROXY` 配置
- **API**: 无 breaking change，错误场景响应体不变但行为改为可重试
- **运维**: 启动命令需传入代理环境变量：`GIT_HTTP_PROXY=... http_proxy=... https_proxy=... uvicorn ...`
