## 1. 公共工具

- [x] 1.1 创建 `backend/analyzer/config.py`，实现 `load_health_spec()` YAML 缓存加载
- [x] 1.2 实现 `weighted_average_score()` 按 sub_metrics 权重计算维度分数
- [x] 1.3 实现 `get_thresholds()` / `get_sub_metrics()` 便捷访问

## 2. code_quality 分析器

- [x] 2.1 实现 `_collect_sources()` 收集 Python/JS/TS/Java/Go 源文件
- [x] 2.2 实现 `_score_cyclomatic_complexity()` 用 radon cc_visit 扫描圈复杂度
- [x] 2.3 实现 `_score_maintainability()` 用 radon mi_visit 计算可维护性指数
- [x] 2.4 实现 `_score_file_size_distribution()` 统计文件行数分布
- [x] 2.5 重写 `CodeQualityAnalyzer.analyze()` 组合三项评分

## 3. test_coverage 分析器

- [x] 3.1 实现 `_find_source_files()` 收集源文件
- [x] 3.2 实现 `_is_test_file()` 按命名模式和目录识别测试文件
- [x] 3.3 实现 `_score_test_file_ratio()` 计算测试文件比例
- [x] 3.4 实现 `_detect_test_frameworks()` 扫描 pytest/jest/vitest/mocha/junit 等
- [x] 3.5 重写 `TestCoverageAnalyzer.analyze()` 组合评分

## 4. architecture 分析器

- [x] 4.1 实现 `_detect_god_classes()` 用 ast 检测方法数>20或行数>500的类
- [x] 4.2 实现 `_analyze_import_coupling()` 统计模块间 import 耦合度
- [x] 4.3 实现 `_check_package_structure()` 检查 __init__.py/setup.py/src 布局
- [x] 4.4 重写 `ArchitectureAnalyzer.analyze()` 组合三项评分

## 5. documentation 分析器

- [x] 5.1 实现 `_score_readme_quality()` 检查 README 的 14 个关键章节
- [x] 5.2 实现 `_score_comment_density()` 统计注释行占比
- [x] 5.3 实现 `_detect_api_documentation()` 检测 Sphinx/MkDocs 等文档配置
- [x] 5.4 重写 `DocumentationAnalyzer.analyze()` 组合评分

## 6. dependency_security 分析器

- [x] 6.1 实现 `_run_bandit()` subprocess 调用 bandit -r -f json
- [x] 6.2 实现 `_run_pip_audit()` subprocess 调用 pip-audit 检查漏洞
- [x] 6.3 实现 `_check_lockfiles()` 检测 12 种 lockfile
- [x] 6.4 重写 `DependencySecurityAnalyzer.analyze()` 组合三项评分

## 7. engineering 分析器

- [x] 7.1 实现 `_check_cicd()` 检测 9 种 CI 配置
- [x] 7.2 实现 `_check_linter()` 检测 9 种 Linter 配置
- [x] 7.3 实现 `_check_git_hygiene()` 检查 .git/.gitignore/.gitattributes
- [x] 7.4 实现 `_check_license()` 检测 8 种 LICENSE 文件名
- [x] 7.5 重写 `EngineeringAnalyzer.analyze()` 组合四项评分

## 8. 依赖安装

- [x] 8.1 安装 radon 6.0.1
- [x] 8.2 安装 bandit 1.9.4
- [x] 8.3 安装 lizard
- [x] 8.4 安装 pip-audit

## 9. 测试与验证

- [x] 9.1 更新 `test_base_analyzer.py`，添加真实项目分析测试
- [x] 9.2 添加 `test_code_quality_on_own_project` 用例
- [x] 9.3 添加 `test_test_coverage_detects_own_tests` 用例
- [x] 9.4 添加 `test_architecture_on_own_project` 用例
- [x] 9.5 添加 `test_documentation_on_own_project` 用例
- [x] 9.6 添加 `test_engineering_on_own_project` 用例
- [x] 9.7 运行 `pytest` 确认 19 个测试全部通过
