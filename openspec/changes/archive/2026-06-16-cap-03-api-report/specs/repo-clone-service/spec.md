## ADDED Requirements

### Requirement: GitHub 仓库浅克隆

系统 SHALL 使用 `git clone --depth 1` 将指定 GitHub URL 克隆到系统临时目录。

#### Scenario: 成功克隆

- **WHEN** 传入有效 GitHub URL `https://github.com/psf/requests`
- **THEN** 仓库被克隆到临时目录，返回 Path 对象

#### Scenario: 无效 URL

- **WHEN** 传入无效 URL 或不存在的仓库
- **THEN** 抛出异常，包含错误描述

### Requirement: 超时控制

系统 SHALL 为克隆操作设置 60 秒超时限制。

#### Scenario: 克隆超时

- **WHEN** 克隆操作超过 60 秒
- **THEN** 进程被终止，返回超时错误

### Requirement: 临时目录自动清理

系统 SHALL 使用 Python tempfile 创建临时目录，克隆完成后由调用方负责清理。

#### Scenario: 临时目录创建

- **WHEN** clone 服务被调用
- **THEN** 创建格式为 `repo-check-XXXXXX` 的临时目录
