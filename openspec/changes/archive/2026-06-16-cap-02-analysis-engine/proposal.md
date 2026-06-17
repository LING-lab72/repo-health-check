## Why

cap-01-project-init 搭建了项目骨架，但 `backend/analyzer/` 下 6 个分析模块的 `analyze()` 方法均为空壳返回 score=0。需要实现真实分析逻辑，使工具能够实际评估 GitHub 仓库的六个维度健康状态。评分规则参照 `sdd/health-spec.yaml` 中的 thresholds 和 weighted_average 公式。

## What Changes

- 重写 6 个分析器模块，实现真实分析逻辑
- 新增 `backend/analyzer/config.py` 统一 YAML 配置加载与评分计算
- 安装 radon / bandit / lizard / pip-audit 分析引擎依赖
- 更新测试，增加真实项目分析验证用例

## Capabilities

### New Capabilities
- `code-quality-analyzer`: radon 圈复杂度 + 可维护性指数 + lizard-like 文件行数分布分析
- `test-coverage-analyzer`: 测试文件比例检测 + 测试框架识别（pytest/jest/vitest 等）
- `architecture-analyzer`: God Class 检测（方法>20/行>500）+ import 耦合度 + 包结构评分
- `documentation-analyzer`: README 质量评分（14 个关键章节）+ 注释密度 + API 文档检测
- `dependency-security-analyzer`: bandit 安全扫描 + pip-audit 漏洞检查 + lockfile 检测
- `engineering-analyzer`: CI/CD + Linter + Gitignore + LICENSE + pre-commit 配置检测

### Modified Capabilities
（无）

## Impact

- 修改：`backend/analyzer/*/analyzer.py`（6 个文件全部重写）
- 新增：`backend/analyzer/config.py`（YAML 加载与计算工具）
- 新增依赖：radon 6.0.1、bandit 1.9.4、lizard、pip-audit
- 更新：`backend/tests/test_base_analyzer.py`（14→19 测试用例）
