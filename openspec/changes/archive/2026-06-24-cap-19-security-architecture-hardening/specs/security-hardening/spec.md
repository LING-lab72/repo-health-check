# Security Hardening

## Purpose

定义 Repo Health Check 的安全基线，包括会话密钥、OAuth CSRF 防护、导出内容转义、可信代理头和运行时工具安全默认值。

## Requirements

### Requirement: Session Secret 必须显式配置

系统 SHALL 要求运行环境显式设置 `SESSION_SECRET`。未设置时，后端 SHALL 拒绝启动，不使用硬编码默认密钥签名 Cookie。

#### Scenario: 未设置 SESSION_SECRET
- **WHEN** 应用启动且环境变量 `SESSION_SECRET` 不存在
- **THEN** session 服务抛出启动错误

#### Scenario: 已设置 SESSION_SECRET
- **WHEN** 环境变量 `SESSION_SECRET` 存在
- **THEN** session 服务使用该值创建签名器

### Requirement: OAuth state 防护

系统 SHALL 在 GitHub OAuth 登录发起时生成随机 state，并通过 HTTP-only Cookie 保存签名后的 state。回调阶段 SHALL 校验请求 state 与 Cookie 中 state 一致。

#### Scenario: OAuth state 匹配
- **WHEN** GitHub 回调携带的 state 与 Cookie 中保存的 state 一致
- **THEN** 系统继续交换 access token 并设置登录 session

#### Scenario: OAuth state 不匹配
- **WHEN** GitHub 回调 state 缺失或不匹配
- **THEN** 系统返回 HTTP 400，不创建登录 session

### Requirement: 导出与 Badge 输出转义

系统 SHALL 对 SVG Badge 和 HTML 导出报告中的动态文本做 HTML 转义。用于 CSS style 的分数、置信度、耗时等数值 SHALL 转换为受控数字并限制范围。

#### Scenario: 导出报告恶意 advice
- **WHEN** AI 诊断建议包含 `<img src=x onerror=alert(1)>`
- **THEN** 导出 HTML 中 SHALL 出现转义文本，不包含可执行标签

#### Scenario: 导出报告恶意 score
- **WHEN** 维度 score 为非数字或超范围值
- **THEN** 系统 SHALL 使用 0-100 范围内的安全数字写入文本和 style

### Requirement: 可信代理头

系统 SHALL 默认不信任客户端提供的 `X-Forwarded-For`。仅当 `TRUST_PROXY_HEADERS=true` 且部署在可信反向代理后时，才可使用该头作为客户端 IP 来源。

#### Scenario: 默认忽略转发头
- **WHEN** 请求包含 `X-Forwarded-For` 但未启用 `TRUST_PROXY_HEADERS`
- **THEN** 系统 SHALL 使用连接来源 IP 而不是转发头

### Requirement: 运行时 npx 安全默认值

系统 SHALL 默认使用 `npx --no-install` 执行 JS/TS 分析工具，避免分析外部仓库时自动下载 npm 包。仅当 `ALLOW_NPX_INSTALL=1` 时，才允许 `npx --yes` 在线安装。

#### Scenario: 默认不下载 npm 包
- **WHEN** 未设置 `ALLOW_NPX_INSTALL=1`
- **THEN** JS 工具执行 SHALL 使用 `npx --no-install`
