## 1. 依赖与环境

- [x] 1.1 添加 httpx + python-dotenv 到 `backend/requirements.txt`
- [x] 1.2 创建 `.env.example` 模板文件（DEEPSEEK_API_KEY / OPENAI_API_KEY）

## 2. AI 诊断模块

- [x] 2.1 创建 `backend/ai/__init__.py`
- [x] 2.2 创建 `backend/ai/diagnose.py`，实现 `ai_diagnose(dimensions, repo_url) -> list[dict]`
- [x] 2.3 实现 API key 检测逻辑（DEEPSEEK_API_KEY > OPENAI_API_KEY）
- [x] 2.4 实现 LLM prompt 模板（基于六维指标生成 JSON 格式建议）
- [x] 2.5 实现 httpx AsyncClient 调用 chat/completions（30s 超时）
- [x] 2.6 实现降级逻辑：无 key / 超时 / 异常 → 本地规则诊断
- [x] 2.7 实现 confidence < 70 → need_human_review 标记

## 3. 集成到分析流程

- [x] 3.1 修改 `backend/analyzer/aggregator.py`，aggregate() 中调用 ai_diagnose()
- [x] 3.2 aggregate() 返回 dict 加入 `ai_diagnosis` 字段
- [x] 3.3 确保 API 响应包含 ai_diagnosis（analyze API 无需修改，自动透传）

## 4. 测试

- [x] 4.1 编写 `backend/tests/test_ai_diagnose.py`：降级逻辑 + 格式化输出
- [x] 4.2 编写 mock LLM API 的集成测试
- [x] 4.3 编写 confidence 标记测试
- [x] 4.4 运行 `pytest` 确认所有测试通过
