## ADDED Requirements

### Requirement: 圈复杂度分析

系统 SHALL 使用 radon 的 `cc_visit` API 对仓库中所有 Python 文件计算圈复杂度，按 `cc_rank` 评级（A-F）。

#### Scenario: 低复杂度项目
- **WHEN** 所有函数圈复杂度 ≤ 5（rank A）
- **THEN** cyclomatic_complexity 评分为 100

#### Scenario: 存在高复杂度函数
- **WHEN** 有函数圈复杂度 > 20
- **THEN** issues 列表包含该函数名、复杂度和所在文件

### Requirement: 可维护性指数分析

系统 SHALL 使用 radon 的 `mi_visit` API 计算每个 Python 文件的 Maintainability Index，按 `mi_rank` 评级 (A/B/C)。

#### Scenario: A 级可维护性
- **WHEN** 平均 MI rank 为 A
- **THEN** 可维护性评分为 95

### Requirement: 文件行数分布分析

系统 SHALL 统计所有源文件行数分布，标记超过 500 行和 1000 行的文件。

#### Scenario: 无超大文件
- **WHEN** 所有文件均 ≤ 300 行平均
- **THEN** file_size_distribution 评分为 95

### Requirement: 加权综合评分

系统 SHALL 按 health-spec.yaml 定义的 sub_metrics 权重计算 code_quality 最终分数。

#### Scenario: 三项指标均衡
- **WHEN** cyclomatic_complexity=90, duplication_rate=85, file_size_distribution=80
- **THEN** 加权平均分 = 90×0.40 + 85×0.35 + 80×0.25 = 85.75
