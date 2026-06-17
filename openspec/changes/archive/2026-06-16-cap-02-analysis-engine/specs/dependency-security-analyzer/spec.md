## ADDED Requirements

### Requirement: Bandit 安全扫描

系统 SHALL 通过 subprocess 调用 `bandit -r -f json` 对仓库进行安全扫描，解析 HIGH/MEDIUM/LOW 级别漏洞。

#### Scenario: 无安全漏洞
- **WHEN** bandit 扫描结果为 0 个问题
- **THEN** known_vulnerabilities 评分为 100

#### Scenario: 存在 HIGH 级别漏洞
- **WHEN** 发现 3 个 HIGH 级别问题
- **THEN** known_vulnerabilities 评分为 max(10, 70 - 3×20) = 10

### Requirement: Lockfile 检测

系统 SHALL 检查 12 种常见 lockfile（requirements.txt/package-lock.json/Pipfile.lock/poetry.lock/yarn.lock/pnpm-lock.yaml/Gemfile.lock/composer.lock/Cargo.lock/go.sum/pom.xml）。

#### Scenario: 多个 lockfile
- **WHEN** 存在 requirements.txt + package-lock.json + poetry.lock
- **THEN** lockfile_present 评分为 100

#### Scenario: 无 lockfile
- **WHEN** 未找到任何 lockfile
- **THEN** lockfile_present 评分为 0，issues 包含警告

### Requirement: Pip-audit 漏洞检查

系统 SHALL 用 pip-audit 检查 requirements.txt 中的已知漏洞依赖。

#### Scenario: 无已知漏洞
- **WHEN** pip-audit 返回 0 个漏洞
- **THEN** dependency_freshness 评分为 100
