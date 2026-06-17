# Repo Clone Service

## Purpose

提供 GitHub 仓库浅克隆能力，作为分析流水线的第一步。使用 `git clone --depth 1` 快速获取仓库代码，支持超时控制、URL 校验、代理自动降级策略。在国内 GFW 网络环境下，自动探测直连并按需回退到代理模式。

## Requirements

### Requirement: GitHub 仓库浅克隆

系统 SHALL 使用 `git clone --depth 1` 将指定 GitHub URL 克隆到系统临时目录。克隆 SHALL 通过 `_run_clone()` 执行，支持可选代理参数。超时 SHALL 为 120 秒。

#### Scenario: 成功克隆

- **WHEN** 传入有效 GitHub URL `https://github.com/psf/requests`
- **THEN** 仓库被克隆到临时目录，返回 Path 对象

#### Scenario: 无效 URL

- **WHEN** 传入无效 URL 或不存在的仓库
- **THEN** 抛出异常，包含错误描述

### Requirement: 超时控制

系统 SHALL 为克隆操作设置 120 秒超时限制。

#### Scenario: 克隆超时

- **WHEN** 克隆操作超过 120 秒
- **THEN** 进程被终止，临时目录被清理，返回超时错误

### Requirement: 临时目录自动清理

系统 SHALL 使用 Python tempfile 创建临时目录，克隆完成后由调用方负责清理。

#### Scenario: 临时目录创建

- **WHEN** clone 服务被调用
- **THEN** 创建格式为 `repo-check-XXXXXX` 的临时目录

### Requirement: 代理配置读取

系统 SHALL 提供 `_get_proxy()` 函数，按优先级从环境变量读取代理 URL：`GIT_HTTP_PROXY` → `https_proxy` → `HTTPS_PROXY` → `http_proxy` → `HTTP_PROXY`。环境变量均不存在时，SHALL 回退到项目根目录 `.env` 文件中同名 key 的值。

#### Scenario: 环境变量优先

- **WHEN** `GIT_HTTP_PROXY=http://127.0.0.1:7890` 存在于环境变量且 `.env` 中也有配置
- **THEN** 返回环境变量中的值

#### Scenario: 回退到 .env 文件

- **WHEN** 环境变量中无任何代理配置且 `.env` 文件包含 `GIT_HTTP_PROXY`
- **THEN** 返回 `.env` 文件中的值

#### Scenario: 无代理配置

- **WHEN** 环境变量和 `.env` 文件中均无代理配置
- **THEN** 返回 `None`

### Requirement: GitHub 直连探测

系统 SHALL 提供 `_test_github_direct()` 函数，使用 `git -c http.proxy="" -c https.proxy="" ls-remote --heads` 测试 GitHub 是否可直连。超时 SHALL 为 15 秒。

#### Scenario: GitHub 可直连

- **WHEN** 网络环境允许直连 GitHub
- **THEN** 函数返回 `True`

#### Scenario: GitHub 不可直连

- **WHEN** GFW 阻断或网络不通
- **THEN** 函数返回 `False`

#### Scenario: 全局代理不干扰探测

- **WHEN** `git config --global http.proxy` 已设置
- **THEN** 探测使用 `-c http.proxy=""` 覆盖全局配置，确保测试直连而非代理连通性

### Requirement: 代理可达性检测

系统 SHALL 提供 `_is_proxy_reachable()` 函数，使用 socket 连接测试代理端口是否在监听。连接超时 SHALL 为 3 秒。

#### Scenario: 代理端口在监听

- **WHEN** 代理地址为 `http://127.0.0.1:7890` 且代理服务正在运行
- **THEN** 函数返回 `True`

#### Scenario: 代理端口未监听

- **WHEN** 代理地址为 `http://127.0.0.1:7890` 但代理服务未启动
- **THEN** 函数返回 `False`

### Requirement: 自动降级克隆策略

系统 SHALL 实现 `clone_repo()` 自动降级克隆策略，按以下顺序尝试：
1. 直连探测（`_test_github_direct()`）→ 成功则无代理克隆
2. 代理回退（`_is_proxy_reachable()`）→ 可达则代理克隆
3. 代理不可达 → 抛出 `CloneError` 含中文提示
4. 无代理配置 → 尝试直连克隆 → 失败则抛出 `CloneError` 含中文提示

#### Scenario: 直连成功

- **WHEN** GitHub 可直连
- **THEN** 执行无代理克隆（显式 `-c http.proxy=""` 清除全局配置）

#### Scenario: 直连失败、代理可用

- **WHEN** GitHub 不可直连且代理可达
- **THEN** 执行 `git clone -c http.proxy=... -c https.proxy=...` 代理克隆

#### Scenario: 直连失败、代理不可达

- **WHEN** GitHub 不可直连且代理已配置但端口未监听
- **THEN** 抛出 `CloneError` 包含中文提示

#### Scenario: 直连失败、无代理配置

- **WHEN** GitHub 不可直连且未配置任何代理
- **THEN** 尝试无代理克隆，失败时抛出 `CloneError` 包含中文提示

### Requirement: git -c flag 代理传递

系统 SHALL 通过 `git -c http.proxy=... -c https.proxy=...` 命令行 flag 传递代理参数给 git clone 命令，不依赖 `git config --global` 全局配置。无代理时 SHALL 显式传递空值以覆盖可能存在的全局代理配置。

#### Scenario: 使用代理克隆

- **WHEN** 需要通过代理克隆且代理地址为 `http://127.0.0.1:7890`
- **THEN** git 命令包含参数 `-c http.proxy=http://127.0.0.1:7890 -c https.proxy=http://127.0.0.1:7890`

#### Scenario: 不使用代理克隆

- **WHEN** 直连成功无需代理
- **THEN** git 命令包含参数 `-c http.proxy= -c https.proxy=`（空值覆盖全局配置）
