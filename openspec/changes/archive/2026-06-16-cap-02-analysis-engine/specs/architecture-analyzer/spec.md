## ADDED Requirements

### Requirement: God Class 检测

系统 SHALL 使用 ast 模块解析 Python 文件，检测方法数 > 20 或行数 > 500 的 God Class。

#### Scenario: 检测到 God Class
- **WHEN** 某个类方法数 = 25，行数 = 600
- **THEN** issues 列表包含该类名、文件路径、方法数和行数

#### Scenario: 无 God Class
- **WHEN** 所有类方法数 ≤ 20 且行数 ≤ 500
- **THEN** 该指标评分为 100

### Requirement: Import 耦合度分析

系统 SHALL 通过 ast 分析 import 语句，统计每个模块导入的内部模块数量，计算平均耦合度。

#### Scenario: 低耦合
- **WHEN** 平均每个模块导入 ≤ 2 个内部模块
- **THEN** module_coupling 评分为 95

#### Scenario: 高耦合警告
- **WHEN** 平均耦合度 > 6
- **THEN** issues 包含 "模块耦合度偏高"

### Requirement: 包结构评分

系统 SHALL 检查 __init__.py 存在性、setup.py/pyproject.toml 包声明、src 布局。

#### Scenario: 标准包结构
- **WHEN** 存在 __init__.py + pyproject.toml + src 目录
- **THEN** package_structure 评分为 100
