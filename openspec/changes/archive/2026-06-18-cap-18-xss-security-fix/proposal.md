## Why

Badge SVG 端点和 Export HTML 端点直接将用户可控的动态数据（仓库 URL、分析维度名称、AI 诊断建议、Badge 标签/值等）未经转义插入 SVG/HTML 模板。攻击者可通过构造恶意仓库名或篡改缓存数据，注入任意 SVG/HTML 标签，实现存储型 XSS 攻击。

此问题被标记为 **P0 安全漏洞（Issue #1）**，需要立即修复。

## What Changes

- `backend/routes/badge.py`：在 `_build_svg()` 中使用 `html.escape()` 对 `label` 和 `value` 参数进行 HTML 转义，防止 SVG 注入
- `backend/routes/export.py`：对所有动态字段（`repo_url`、`badge_level`、`dimension`、`advice`、`severity`、`analyzed_at`）使用 `html.escape()` 转义后再插入 HTML 模板
- `backend/routes/export.py`：导出文件名仅允许安全字符集 `[a-zA-Z0-9\-._]`，防止 Content-Disposition 头注入
- `backend/routes/export.py`：将局部变量 `html` 重命名为 `html_content`，避免与 `import html` 模块名冲突

## Capabilities

### New Capabilities

- 无（安全修复，不新增功能）

### Modified Capabilities

- `badge-api`：Badge SVG 生成增加 HTML 转义层，防止 SVG 注入攻击

## Impact

- **Frontend**: 无影响
- **Backend**: 修改 2 个文件（`routes/badge.py` + `routes/export.py`）
- **API**: 无 breaking change（正常输入输出不变，仅过滤恶意字符）
- **Dependencies**: 无（`html` 为 Python 标准库）
