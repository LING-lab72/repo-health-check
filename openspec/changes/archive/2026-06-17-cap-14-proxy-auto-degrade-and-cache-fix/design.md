## Context

项目在中国网络环境下遇到三个串联问题：

1. **GFW 阻断 GitHub**：`git clone` 触发 `Recv failure: Connection was reset` 或 `schannel: failed to receive handshake, SSL/TLS connection failed`
2. **代理无法传递到 subprocess**：`git config --global http.proxy` 对 Python `subprocess.run` 调用的 git 命令无效；`load_dotenv()` 加载的 `.env` 变量在 uvicorn worker 进程中无法可靠传递给 subprocess
3. **错误缓存不可恢复**：`analyze.py` 缓存命中后无论成功还是错误都直接返回，导致第一次网络故障后，即使网络恢复也无法重新检测同一仓库

所有修改已完成并通过验证，此设计文档记录技术决策。

## Goals / Non-Goals

**Goals:**
- git clone 在有代理时自动使用代理，无代理时自动尝试直连
- 直连和代理都不可用时给出清晰中文提示，而非底层 SSL 错误
- 错误结果不阻塞后续重新检测
- 代理配置通过 `git -c` flag 传递，不依赖全局 git 配置

**Non-Goals:**
- 不改变克隆超时时间或 TTL 配置
- 不引入 Redis 等外部缓存替代内存缓存
- 不新增 API 端点
- 不修改前端代码（错误提示由后端响应体驱动）

## Decisions

### D1: 自动降级策略——直连优先、代理回退

**决策**：`clone_repo()` 执行三步降级：
1. `_test_github_direct()` 用 `git -c http.proxy="" -c https.proxy="" ls-remote` 探测直连（绕过全局代理）
2. 直连成功 → `_run_clone(proxy=None)` 无代理克隆
3. 直连失败 → `_is_proxy_reachable()` 检查代理 → `_run_clone(proxy=proxy_url)` 代理克隆
4. 代理不可达或无代理 → 友好中文错误

**替代方案考虑**：
- ❌ 仅支持代理模式 — 国内 GitHub 偶尔可以直连，强制代理增加延迟和依赖
- ❌ 仅支持直连模式 — 在 GFW 环境下完全不可用
- ❌ 让用户手动选择模式 — 增加操作负担，应自动检测

### D2: `git -c` flag 传递代理而非全局配置

**决策**：通过 `git -c http.proxy=http://... -c https.proxy=http://...` 在命令行直接传递代理参数给每次 git 调用。不使用 `git config --global`。

**替代方案考虑**：
- ❌ `git config --global http.proxy` — 在 Python subprocess 中不可靠，uvicorn 进程与 shell 环境隔离
- ❌ `subprocess.run(env={...})` 注入环境变量 — `git` 不读取 `http_proxy` 环境变量（schannel 后端）
- ❌ `.gitconfig` 文件写入 — 需要清理，并发时可能冲突

### D3: 直连探测绕过全局代理

**决策**：`_test_github_direct()` 使用 `git -c http.proxy="" -c https.proxy=""` 显式清除全局代理配置，确保直连测试不受 `git config --global` 干扰。

**替代方案考虑**：
- ❌ 直接 `git ls-remote` 不带 `-c` — 如果全局配置了代理，测试结果不准确（测试的是代理连通性而非直连）
- ❌ `subprocess.run(env={...})` 清除环境变量 — git schannel 后端不依赖环境变量

### D4: 错误缓存命中时 invalidate 而非返回

**决策**：`/api/analyze` 端点缓存命中但结果包含 `_error` 字段时，调用 `cache.invalidate(repo_url)` 清除后继续执行实际检测。与 `/api/analyze/local` 已有的处理保持一致。

**替代方案考虑**：
- ❌ 错误结果设置更短 TTL — 增加 cache.py 复杂度，且 30 分钟内网络可能已恢复
- ❌ 前端增加"重试"按钮 force_sync — 治标不治本，force_sync 也被缓存拦截
- ❌ 完全不缓存错误 — 合理，但后台任务错误需要某种方式记录状态（pending→failed 转换）

### D5: `.env` 代理配置 + 启动时环境变量双重保障

**决策**：`.env` 中新增 `GIT_HTTP_PROXY` 配置，`_get_proxy()` 读取环境变量和 .env 文件。但启动 uvicorn 时仍需传入 `GIT_HTTP_PROXY=... http_proxy=... https_proxy=...` 环境变量，因为 `load_dotenv()` 加载的变量在 uvicorn worker 进程中可能无法传递给 subprocess。

**替代方案考虑**：
- ❌ 仅依赖 `.env` — 实测 `load_dotenv()` 加载的变量在 uvicorn 子进程传递链中不可靠
- ❌ 仅依赖启动命令行 — 缺少配置文件持久化，重启需手动输入
- ✅ 双保险：`.env` 持久化配置 + 启动命令行显式传递

## Risks / Trade-offs

- **[直连探测耗时]** → `_test_github_direct()` 需 15 秒超时，在网络完全不通时增加首次请求延迟。权衡：15 秒等待优于直接超时 120 秒 clone 失败。
- **[代理端口检测假阳性]** → `_is_proxy_reachable()` 仅检测端口是否在监听，不验证代理功能是否正常。权衡：完整的代理功能测试太慢，端口监听已足够判断 Clash 是否启动。
- **[错误重试风暴]** → 清除错误缓存后，如果网络持续不通，每次请求都会重新检测失败。权衡：比永远返回旧错误好；且检测耗时约 15 秒，不会形成风暴。
- **[git -c 不支持 SSH]** → 当前仅支持 HTTPS 代理，SSH clone 不受影响（但项目本身仅支持 HTTPS URL）。
