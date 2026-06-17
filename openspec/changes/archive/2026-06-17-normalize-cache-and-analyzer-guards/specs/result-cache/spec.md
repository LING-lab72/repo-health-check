## ADDED Requirements

### Requirement: URL 规范化

系统 SHALL 提供 `normalize_url(repo_url)` 静态方法，对 URL 执行 `strip()` → `rstrip("/")` → `rstrip(".git")`（大小写不敏感）三步规范化。

#### Scenario: 尾部斜杠规范化
- **WHEN** 传入 `"https://github.com/user/repo/"`
- **THEN** 返回 `"https://github.com/user/repo"`

#### Scenario: .git 后缀规范化
- **WHEN** 传入 `"https://github.com/user/repo.git"`
- **THEN** 返回 `"https://github.com/user/repo"`

#### Scenario: 空白字符规范化
- **WHEN** 传入 `"  https://github.com/user/repo  "`
- **THEN** 返回 `"https://github.com/user/repo"`

### Requirement: 缓存条目失效

系统 SHALL 提供 `invalidate(repo_url)` 公共方法，从缓存中移除指定 URL 的条目。该方法 SHALL 在锁保护下执行。

#### Scenario: 失效已存在条目
- **WHEN** 调用 `invalidate("https://github.com/user/repo")` 且该条目在缓存中
- **THEN** 该条目被移除，后续 `get()` 返回 None

#### Scenario: 失效不存在条目
- **WHEN** 调用 `invalidate("https://github.com/user/nonexistent")` 且该条目不在缓存中
- **THEN** 无副作用，不抛异常

## MODIFIED Requirements

### Requirement: 结果缓存

系统 SHALL 实现内存缓存，key 为 `normalize_url(repo_url)` 规范化后的 URL，value 为分析结果，TTL 为 30 分钟。

#### Scenario: 缓存命中
- **WHEN** 查询已分析仓库且距上次分析 < 30 分钟
- **THEN** 直接返回缓存结果，不重新分析

#### Scenario: 缓存过期
- **WHEN** 查询已分析仓库但距上次分析 ≥ 30 分钟
- **THEN** 重新分析并更新缓存
