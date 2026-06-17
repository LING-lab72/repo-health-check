## Context

cap-01 完成后，6 个分析器均为桩代码。需要基于 `sdd/health-spec.yaml` 的评分规则实现真实分析逻辑。所有分析器共享 `BackendAnalyzer` 接口，统一返回 `AnalysisResult(dimension, score, details, issues)`。

## Goals / Non-Goals

**Goals:**
- 实现 6 个维度的真实分析逻辑
- 评分结果符合 health-spec.yaml 的 weighted_average 公式
- 分析引擎依赖全部安装可用
- 测试覆盖所有分析器

**Non-Goals:**
- 不接入 OpenAI/DeepSeek AI 分析（documentation 的 AI 标注暂用自定义规则代替）
- 不修改 health-spec.yaml 评分规则

## Decisions

### 1. 配置加载：单例缓存

**选择**：`config.py` 使用 `@lru_cache` 缓存 YAML 加载，`weighted_average_score()` 读取 sub_metrics 的 weight 动态计算。

**理由**：每次分析都需读配置，缓存避免重复 I/O。`weighted_average_score()` 返回 score + sub_scores + missing_keys，调用方无需关心权重细节。

### 2. code_quality：radon.raw_analyze + cc_visit + mi_visit

**选择**：用 `radon` 的内置 API（非 CLI），逐文件扫描 `.py` 文件。圈复杂度用 `cc_rank` 评级映射分数（A→100, F→10），可维护性指数用 `mi_rank` 映射。

**理由**：API 方式比 subprocess 更稳定，直接操作 Python 对象避免 JSON 解析。

### 3. test_coverage：文件系统扫描 + 模式匹配

**选择**：不解析 coverage.xml，而是通过测试文件命名模式（test_*/_test/*.spec/*.test）统计比例，通过 rglob 搜索框架配置文件检测框架。

**理由**：coverage.xml 需要先跑测试，不适合静态分析。文件比例是更通用的代理指标。

### 4. architecture：AST + God Class 检测

**选择**：用 `ast` 模块解析 Python 文件，检测方法数 >20 或行数 >500 的 God Class。import 耦合度统计每个模块的内部 import 数量。

**理由**：ast 是标准库，无需额外依赖。针对 Python 做深度分析，其他语言仅做文件统计。

### 5. documentation：正则 + 文本分析

**选择**：README 质量用 14 个关键章节关键词匹配（install/usage/examples 等），注释密度通过行首注释符号计数，API 文档通过文件系统查找 mkdocs.yml/conf.py 等。

**理由**：纯文本分析，速度快，结果可解释。

### 6. dependency_security：subprocess 调用外部工具

**选择**：bandit 通过 `subprocess.run` 调用解析 JSON 输出，pip-audit 同样方式。

**理由**：bandit 和 pip-audit 的 Python API 不稳定，subprocess + JSON 解析更可靠。

### 7. engineering：文件系统检测

**选择**：检查 10 种 CI 配置文件存在性、9 种 Linter 配置、8 种 LICENSE 文件名。

**理由**：纯文件存在检测，零计算开销。

## Risks / Trade-offs

- **[radon 版本兼容]** `cc_visit` 返回对象的 `filename` 属性已改为 `fullname` → 在代码中跟踪文件名
- **[bandit 扫描超时]** 大型仓库可能超时 → 设置 120s 超时，超时返回默认分数
- **[pip-audit 依赖更新]** 新版本可能改变 JSON 格式 → 用 try/except JSONDecodeError 兜底
