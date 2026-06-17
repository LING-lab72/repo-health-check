## ADDED Requirements

### Requirement: 健康评分配置文件

系统 SHALL 在 `sdd/` 目录下创建 `health-spec.yaml`，定义六个维度的评分权重、阈值和计算公式。

#### Scenario: YAML 文件存在且可解析

- **WHEN** 后端读取 `sdd/health-spec.yaml`
- **THEN** YAML 解析成功，返回包含六个维度的字典结构

### Requirement: 维度定义

`health-spec.yaml` SHALL 包含六个维度的配置，每个维度 MUST 包含 `name`、`weight`（权重百分比）、`thresholds`（阈值分级：excellent/good/warning/critical）。

#### Scenario: 权重总和

- **WHEN** 校验六个维度的 `weight` 值
- **THEN** 权重总和等于 1.0（100%）

### Requirement: 评分公式

每个维度 SHALL 定义 `formula` 字段，指定如何根据子指标计算该维度分数（如加权平均、最低分等）。

#### Scenario: 公式为加权平均

- **WHEN** 维度 `formula` 设置为 `weighted_average`
- **THEN** 该维度分数 = Σ(子指标分值 × 子指标权重) / Σ(子指标权重)

### Requirement: 整体健康分计算

系统 SHALL 根据各维度分数和权重计算整体健康分（0-100），公式：`health_score = Σ(维度分数 × 维度权重)`。

#### Scenario: 等权重计算

- **WHEN** 六个维度分数为 [80, 70, 90, 60, 85, 75]，权重均为 1/6
- **THEN** 整体健康分 = (80+70+90+60+85+75)/6 = 76.67

### Requirement: Badge 等级映射

系统 SHALL 根据整体健康分映射到 Badge 等级：≥80 A级（绿色）、≥60 B级（黄色）、≥40 C级（橙色）、<40 D级（红色）。

#### Scenario: A 级判定

- **WHEN** 整体健康分 = 85
- **THEN** Badge 等级为 A，颜色为绿色
