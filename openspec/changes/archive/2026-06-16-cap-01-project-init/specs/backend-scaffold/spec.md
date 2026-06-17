## ADDED Requirements

### Requirement: FastAPI 应用骨架

系统 SHALL 在 `backend/` 目录下初始化 FastAPI 应用，包含基础中间件（CORS、日志）和健康检查端点。

#### Scenario: 服务启动

- **WHEN** 执行 `uvicorn main:app --reload`
- **THEN** FastAPI 服务在 `http://localhost:8000` 启动，`/health` 端点返回 `{"status": "ok"}`

#### Scenario: CORS 配置

- **WHEN** 前端 `http://localhost:5173` 发起跨域请求
- **THEN** 后端响应包含正确的 `Access-Control-Allow-Origin` 头

### Requirement: 分析模块接口规范

系统 SHALL 定义 `BaseAnalyzer` 抽象基类，所有六个维度分析模块 MUST 实现相同的 `analyze(repo_path: Path) -> AnalysisResult` 接口。

#### Scenario: 模块统一签名

- **WHEN** 检查任意分析模块（如 `code_quality`、`dependency_security`）
- **THEN** 该模块 MUST 实现 `analyze()` 方法，返回 `AnalysisResult` 类型（`dimension: str, score: float, details: dict, issues: list`）

### Requirement: 六大维度模块目录

系统 SHALL 在 `backend/analyzers/` 下创建六个独立子包：`code_quality`、`test_coverage`、`architecture`、`documentation`、`dependency_security`、`engineering`，每个子包包含 `__init__.py` 和 `analyzer.py`。

#### Scenario: 模块导入

- **WHEN** 从 `backend.analyzers` 导入任意分析模块
- **THEN** 导入成功，模块暴露 `analyze` 函数

### Requirement: 统一 JSON 响应格式

所有 API 端点 SHALL 返回统一 JSON 格式：`{"code": int, "message": str, "data": ...}`。

#### Scenario: 正常响应

- **WHEN** 调用 `/api/analyze` 且分析成功
- **THEN** 返回 `{"code": 0, "message": "success", "data": {"repo": "...", "results": [...]}}`

#### Scenario: 错误响应

- **WHEN** 调用 API 传入非法参数
- **THEN** 返回 `{"code": 400, "message": "Invalid repository URL", "data": null}`

### Requirement: 依赖声明文件

系统 SHALL 在 `backend/` 下创建 `requirements.txt`，声明 FastAPI、uvicorn、radon、bandit、pip-audit、lizard、pyyaml 等核心依赖。

#### Scenario: 依赖安装

- **WHEN** 执行 `pip install -r requirements.txt`
- **THEN** 所有依赖成功安装，`uvicorn --version` 正常输出
