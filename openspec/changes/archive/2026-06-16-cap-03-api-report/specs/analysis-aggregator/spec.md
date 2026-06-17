## ADDED Requirements

### Requirement: 六维分析调用

系统 SHALL 串行调用 6 个维度分析器（code_quality / test_coverage / architecture / documentation / dependency_security / engineering），每个分析器返回 AnalysisResult。

#### Scenario: 所有分析器成功

- **WHEN** 传入有效仓库路径
- **THEN** 返回 6 个 AnalysisResult 的列表，每个包含 dimension/score/details/issues

#### Scenario: 单个分析器失败

- **WHEN** 某个分析器抛出异常
- **THEN** 该维度 score=0，issues 包含错误信息，其余维度正常

### Requirement: 加权总分计算

系统 SHALL 从 health-spec.yaml 读取各维度权重，按 weighted_average 公式计算 health_score。

#### Scenario: 等权重计算

- **WHEN** 六个维度分数为 [80, 70, 90, 60, 85, 75]，权重均为健康值
- **THEN** health_score = Σ(维度分数 × 维度权重)

### Requirement: Badge 等级映射

系统 SHALL 按 health-spec.yaml 的 badge_levels 将 health_score 映射为等级和颜色。

#### Scenario: A 级判定

- **WHEN** health_score = 85
- **THEN** badge_level = "A"，badge_color = "brightgreen"

#### Scenario: D 级判定

- **WHEN** health_score = 35
- **THEN** badge_level = "D"，badge_color = "red"

### Requirement: 聚合结果格式

系统 SHALL 返回统一格式的聚合结果，包含 repo_url / health_score / badge_level / badge_color / dimensions[] / analyzed_at。

#### Scenario: 完整聚合结果

- **WHEN** 分析完成
- **THEN** 返回 JSON 包含所有必需字段，dimensions 为各维度 AnalysisResult 的列表
