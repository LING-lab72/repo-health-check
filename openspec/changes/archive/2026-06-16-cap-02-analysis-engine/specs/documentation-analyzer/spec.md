## ADDED Requirements

### Requirement: README 质量评分

系统 SHALL 检测 README 文件，检查 14 个关键章节（install/usage/getting started/quick start/example/contributing/license/documentation/api/overview/description/features/configuration/setup/requirements），按找到比例评分。

#### Scenario: 完整 README
- **WHEN** README 包含 >=10 个关键章节、有标题结构、有代码块、有链接
- **THEN** readme_quality 评分 ≥ 80

#### Scenario: 缺少 README
- **WHEN** 未找到 README 文件
- **THEN** readme_quality 评分为 0，issues 包含 "未找到 README 文件"

### Requirement: 注释密度分析

系统 SHALL 统计源文件中注释行占比（comment_lines / total_lines），合理范围 10%-40%。

#### Scenario: 合理注释密度
- **WHEN** 注释占比在 10%-40% 之间
- **THEN** comment_ratio 评分为 90

#### Scenario: 注释过少
- **WHEN** 注释占比 < 2%
- **THEN** comment_ratio 评分为 20，issues 包含 "注释密度过低"

### Requirement: API 文档检测

系统 SHALL 检测 API 文档配置（Sphinx/MkDocs/Docusaurus/JSDoc 等）和 docs/ 目录存在性。

#### Scenario: 完整文档套件
- **WHEN** 存在 mkdocs.yml 和 docs/ 目录
- **THEN** api_documentation 评分为 90
