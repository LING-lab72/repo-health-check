# Persistent Storage

## Purpose

持久化保存分析历史、排行榜投票和投票冷却状态。存储层对路由暴露稳定函数接口，底层使用 SQLite，避免 JSON 文件全量加载在多进程部署中的数据不一致问题。

## Requirements

### Requirement: SQLite 持久化

系统 SHALL 使用 SQLite 数据库保存历史分析结果、投票计数和投票冷却信息。默认数据库路径 SHALL 为 `data/repo_health.db`，并允许通过 `REPO_HEALTH_DATA_DIR` 或 `REPO_HEALTH_DB_FILE` 环境变量覆盖。

#### Scenario: 默认数据库初始化
- **WHEN** 应用启动且 `data/repo_health.db` 不存在
- **THEN** 存储层创建 SQLite 数据库和所需表结构

#### Scenario: 测试数据库隔离
- **WHEN** 设置 `REPO_HEALTH_DB_FILE`
- **THEN** 存储层使用指定数据库文件，不写入生产运行数据

### Requirement: 历史结果查询

系统 SHALL 提供 `save_entry()`、`get_all()`、`get_history()` 和 `get_by_url_hash()` 函数，保持与旧 JSON 存储接口兼容。

#### Scenario: 排行榜最新结果
- **WHEN** 同一 repo_url 有多次分析记录
- **THEN** `get_all()` 返回该仓库 analyzed_at 最新的记录，并按 health_score 降序排列

#### Scenario: 历史趋势
- **WHEN** 查询某个 repo_url 的历史记录
- **THEN** `get_history()` 按 analyzed_at 升序返回所有记录

### Requirement: 投票持久化与冷却

系统 SHALL 持久化每个 repo_url 的投票计数，并按 voter_id 记录最近投票时间，防止同一 voter_id 在冷却窗口内重复投票。

#### Scenario: 首次投票
- **WHEN** voter_id 首次给 repo_url 投票
- **THEN** 投票计数加 1，并返回新计数

#### Scenario: 冷却窗口内重复投票
- **WHEN** 同一 voter_id 在 60 秒内再次给同一 repo_url 投票
- **THEN** `cast_vote()` 返回 None，计数不增加

### Requirement: 旧 JSON 数据迁移

系统 SHALL 在 SQLite 数据库为空且 `data/history.json` 或 `data/votes.json` 存在时，尝试一次性导入旧数据。

#### Scenario: 旧历史导入
- **WHEN** SQLite history 表为空且存在合法 history.json
- **THEN** 存储层导入旧历史记录

#### Scenario: 旧投票导入
- **WHEN** SQLite votes 表为空且存在合法 votes.json
- **THEN** 存储层导入旧投票计数
