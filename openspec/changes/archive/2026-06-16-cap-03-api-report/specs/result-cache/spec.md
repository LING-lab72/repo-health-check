## ADDED Requirements

### Requirement: 结果缓存

系统 SHALL 实现内存缓存，key 为 repo_url，value 为分析结果，TTL 为 30 分钟。

#### Scenario: 缓存命中

- **WHEN** 查询已分析仓库且距上次分析 < 30 分钟
- **THEN** 直接返回缓存结果，不重新分析

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
