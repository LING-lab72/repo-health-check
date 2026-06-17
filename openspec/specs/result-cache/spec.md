# Result Cache

## Purpose

内存分析结果缓存服务，减少重复 git clone 和分析开销，30 分钟 TTL，线程安全。

## Requirements

### Requirement: 结果缓存

系统 SHALL 实现内存缓存，key 为 `normalize_url(repo_url)` 规范化后的 URL，value 为分析结果，TTL 为 30 分钟。错误结果（含 `_error` 字段）同样会被缓存，但调用方 SHALL 在检测到错误缓存时主动调用 `invalidate()` 清除后重新检测，而非直接返回错误。

#### Scenario: 缓存命中成功结果

- **WHEN** 查询已分析仓库且距上次分析 < 30 分钟且结果无 `_error`
- **THEN** 直接返回缓存结果，不重新分析

#### Scenario: 缓存命中错误结果

- **WHEN** 查询已分析仓库且距上次分析 < 30 分钟但结果含 `_error`
- **THEN** 缓存层返回错误结果，调用方可选择 `invalidate()` 后重新检测

#### Scenario: 缓存过期

- **WHEN** 查询已分析仓库但距上次分析 ≥ 30 分钟
- **THEN** 重新分析并更新缓存

### Requirement: 缓存容量控制

系统 SHALL 限制最大缓存条目数为 100，超出时清理所有过期条目。

#### Scenario: 缓存满载清理

- **WHEN** 缓存条目数达到 100 且有新条目要写入
- **THEN** 清理所有过期条目（TTL 超过 30 分钟的），释放空间后写入新条目

### Requirement: 线程安全

系统 SHALL 使用 threading.Lock 保护缓存读写操作，防止并发写入冲突。

#### Scenario: 并发写入同一 key

- **WHEN** 两个请求同时分析同一仓库
- **THEN** 第一个写入成功，第二个检测到 key 存在后直接读取

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
