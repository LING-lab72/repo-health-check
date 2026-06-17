## MODIFIED Requirements

### Requirement: 结果缓存

系统 SHALL 实现内存缓存，key 为 `normalize_url(repo_url)` 规范化后的 URL，value 为分析结果，TTL 为 30 分钟。错误结果（含 `_error` 字段）同样会被缓存，但调用方（如 analyze-api 端点）SHALL 在检测到错误缓存时主动调用 `invalidate()` 清除后重新检测，而非直接返回错误。

#### Scenario: 缓存命中成功结果
- **WHEN** 查询已分析仓库且距上次分析 < 30 分钟且结果无 `_error`
- **THEN** 直接返回缓存结果，不重新分析

#### Scenario: 缓存命中错误结果——由调用方决定处理策略
- **WHEN** 查询已分析仓库且距上次分析 < 30 分钟但结果含 `_error`
- **THEN** 缓存层返回错误结果，调用方可选择 `invalidate()` 后重新检测
