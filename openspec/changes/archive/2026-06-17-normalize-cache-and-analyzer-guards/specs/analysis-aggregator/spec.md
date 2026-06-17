## ADDED Requirements

### Requirement: Analyzer 文件扫描上限

code_quality、architecture、test_coverage、documentation、dependency_security 五个 analyzer 在收集源文件时 SHALL 设置 `MAX_FILES` 常量限制最大扫描文件数。code_quality SHALL 为 `MAX_FILES = 100`，其余四个 SHALL 为 `MAX_FILES = 200`。engineering analyzer 无需限制（不遍历源文件）。

#### Scenario: 超大仓库文件截断
- **WHEN** 仓库包含 5000 个 Python 文件，architecture analyzer 的 `_collect_python_files()` 执行
- **THEN** 收集前 200 个文件后停止，不继续遍历

#### Scenario: 小仓库正常扫描
- **WHEN** 仓库仅有 30 个源文件
- **THEN** 全部 30 个文件被收集，不受 MAX_FILES 限制影响
