## ADDED Requirements

### Requirement: 测试文件比例检测

系统 SHALL 通过文件名和目录模式识别测试文件（test_*.py、*_test.py、*.spec.ts、*.test.ts 等），计算测试文件数 / 源文件数比例。

#### Scenario: 高测试覆盖
- **WHEN** 测试文件比例 ≥ 0.5
- **THEN** test_file_ratio 评分为 95

#### Scenario: 无测试文件
- **WHEN** 未发现任何测试文件
- **THEN** test_file_ratio 评分为 0，issues 包含 "测试文件比例过低"

### Requirement: 测试框架检测

系统 SHALL 扫描仓库检测测试框架配置：pytest（conftest.py/tox.ini）、jest（jest.config.）、vitest（vitest.config.）、unittest（import unittest）、JUnit（@Test）、Go testing（func Test）。

#### Scenario: 检测到 pytest
- **WHEN** 仓库包含 conftest.py 文件
- **THEN** detected_frameworks 包含 "pytest"

#### Scenario: 多框架并存
- **WHEN** 仓库同时使用 pytest 和 jest
- **THEN** test_framework_detected 评分为 90

### Requirement: 覆盖率配置检测

系统 SHALL 检查 coverage 配置文件（.coveragerc/coverage.json）存在性作为覆盖率代理指标。

#### Scenario: 有覆盖率配置
- **WHEN** 存在 .coveragerc 或 pyproject.toml 中的 coverage 配置
- **THEN** coverage_percentage 评分额外增加
