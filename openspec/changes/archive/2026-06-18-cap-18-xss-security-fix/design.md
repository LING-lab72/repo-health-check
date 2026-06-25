## Context

项目后端有两个端点直接拼接用户可控数据到 SVG/HTML 模板中：

1. **Badge SVG（`/api/badge/{repo_hash}`）**：将 `label` 和 `value` 直接插入 SVG `<text>` 标签
2. **Export HTML（`/api/export/{repo_hash}`）**：将仓库 URL、维度名称、AI 建议文本、Badge 等级等直接插入 HTML 模板

攻击向量：攻击者可以 clone 一个仓库名为 `"><script>alert(1)</script>` 的恶意仓库，分析结果缓存后，访问 Badge 或 Export 端点即可触发 XSS。

此问题标记为 P0（优先级最高的安全缺陷），需要立即修复。所有修改已完成，此设计文档记录安全决策。

## Goals / Non-Goals

**Goals:**
- 消除 Badge SVG 端点的 XSS 注入风险
- 消除 Export HTML 端点的 XSS 注入风险
- 消除 Export 端点的 Content-Disposition 头注入风险
- 修复 `html` 变量名遮蔽标准库模块的问题

**Non-Goals:**
- 不引入 Web 应用防火墙（WAF）或全局中间件级 XSS 过滤（本次为定点修复）
- 不添加 CSP（Content Security Policy）响应头（可作为后续加固项）
- 不修改前端 XSS 防护（React 18 默认转义 JSX 输出，前端已有天然防护）

## Decisions

### D1: html.escape() 定点转义而非全局中间件

**决策**：在数据插入模板前，使用 Python 标准库 `html.escape(text, quote=True)` 对每个动态字段逐一转义。

**替代方案考虑**：
- ❌ 全局中间件过滤请求/响应 — 过于宽泛，可能误伤合法内容（如 Markdown 中的 HTML 标签），且对 SVG 模板不适用
- ❌ Jinja2 模板引擎自动转义 — 当前模板为 f-string 拼接，迁移到 Jinja2 改动过大
- ✅ html.escape() 定点转义 — 最小改动、最精确防护，Python 标准库零依赖，`quote=True` 同时转义双引号防止属性逃逸

### D2: Content-Disposition 文件名白名单过滤

**决策**：导出文件名仅允许 `[a-zA-Z0-9\-._]`，其余字符替换为 `_`。

**替代方案考虑**：
- ❌ RFC 5987 `filename*=UTF-8''...` 编码 — 实现复杂，部分浏览器兼容性不佳
- ❌ 仅过滤 `\r\n` — 不够彻底，攻击者可能利用其他特殊字符
- ✅ 白名单字符集 — 最简单可靠的方案，GitHub 仓库名本身就只包含字母、数字、连字符和点

### D3: html_content 变量名消除模块遮蔽

**决策**：将导出函数中的局部变量 `html = f"""..."""` 重命名为 `html_content`，避免与顶部 `import html` 模块名冲突。

**替代方案考虑**：
- ❌ `import html as html_mod` — 非标准命名惯例，降低可读性
- ❌ 使用 `from html import escape` — 当前代码多处使用 `html.escape()`，改动量更大
- ✅ 重命名局部变量 — 最小改动，消除遮蔽，`html_content` 语义清晰

## Risks / Trade-offs

- **[转义后宽度计算偏差]** → `html.escape()` 会将 `<` 转为 `&lt;`（4 字符），`_char_width()` 使用转义后的字符串计算 SVG 宽度。正常仓库名不含 HTML 特殊字符，因此对绝大多数用户无影响；极端情况下（含 `&` 的仓库名），Badge 宽度会略大于实际需要，视觉上表现为右侧留白稍多——可接受的 trade-off。
- **[后续端点遗漏]** → 本次仅修复 Badge 和 Export 两个端点。若未来新增端点也拼接用户数据到模板中，需同步应用转义。缓解：在 AGENTS.md 中标注此安全规范。
- **[无自动化测试覆盖]** → 本次修复未新增 XSS 单元测试。建议后续补充安全测试用例（如注入 `<script>` 的仓库 URL）。
