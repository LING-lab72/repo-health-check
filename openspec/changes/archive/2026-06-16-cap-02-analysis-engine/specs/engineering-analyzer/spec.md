## ADDED Requirements

### Requirement: CI/CD 配置检测

系统 SHALL 检测常见 CI/CD 配置（GitHub Actions/GitLab CI/Travis/Jenkins/CircleCI/Azure Pipelines/Drone）。

#### Scenario: 多 CI 配置
- **WHEN** 存在 .github/workflows/*.yml 和 .gitlab-ci.yml
- **THEN** cicd_config 评分为 95

#### Scenario: 无 CI 配置
- **WHEN** 未找到任何 CI 配置文件
- **THEN** cicd_config 评分为 0

### Requirement: Linter 配置检测

系统 SHALL 检测 9 种 Linter/Formatter 配置（flake8/eslint/prettier/editorconfig/pre-commit/pylint/stylelint/golangci/checkstyle）。

#### Scenario: 多 Linter 配置
- **WHEN** 存在 .flake8 + .eslintrc.cjs + .prettierrc
- **THEN** linter_config 评分为 95

### Requirement: Git 规范检测

系统 SHALL 检查 .git 目录、.gitignore 质量（含 node_modules/__pycache__/.env 等关键排除项）、.gitattributes。

#### Scenario: 规范 Git 仓库
- **WHEN** 存在 .git + .gitignore（含关键排除项）+ .gitattributes
- **THEN** git_hygiene 评分 ≥ 70

#### Scenario: 缺少 .gitignore
- **WHEN** .gitignore 不存在
- **THEN** issues 包含 "缺少 .gitignore 文件"

### Requirement: LICENSE 检测

系统 SHALL 检查 8 种常见 LICENSE 文件名。

#### Scenario: LICENSE 存在
- **WHEN** 根目录存在 LICENSE 文件
- **THEN** license_present 评分为 100

#### Scenario: LICENSE 缺失
- **WHEN** 未找到任何 LICENSE 文件
- **THEN** license_present 评分为 0
