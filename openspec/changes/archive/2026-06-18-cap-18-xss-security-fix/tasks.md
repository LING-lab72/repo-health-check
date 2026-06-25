## 1. Badge SVG XSS 防护

- [x] 1.1 `badge.py` 顶部新增 `import html` 标准库导入
- [x] 1.2 `_build_svg()` 函数中，使用 `html.escape(label, quote=True)` 和 `html.escape(value, quote=True)` 转义动态文本
- [x] 1.3 SVG 宽度计算使用转义后的字符串（`_char_width(label_safe)` / `_char_width(value_safe)`）
- [x] 1.4 SVG 模板插值使用转义后的变量（`label=label_safe` / `value=value_safe`）

## 2. Export HTML XSS 防护

- [x] 2.1 `export.py` 顶部新增 `import html` 标准库导入
- [x] 2.2 对 `repo_url` 使用 `html.escape(str(repo), quote=True)` 转义
- [x] 2.3 对 `badge_level` 使用 `html.escape(str(badge), quote=True)` 转义
- [x] 2.4 对 `analyzed_at` 使用 `html.escape(str(...), quote=True)` 转义
- [x] 2.5 对维度名称 `dimension` 使用 `html.escape(str(d.get('dimension', '')), quote=True)` 转义
- [x] 2.6 对 AI 建议文本 `advice` 使用 `html.escape(str(s.get('advice', '')), quote=True)` 转义
- [x] 2.7 对 `severity` 等级使用 `html.escape(str(s.get('severity', '')).upper(), quote=True)` 转义
- [x] 2.8 使用 `d.get('score', 0)` / `s.get('confidence', 0)` 等安全取值代替直接下标访问

## 3. Content-Disposition 头注入防护

- [x] 3.1 定义安全字符白名单 `[a-zA-Z0-9\-._]`
- [x] 3.2 仓库 URL 处理后，非白名单字符替换为 `_`
- [x] 3.3 最终文件名格式：`{safe_name}-health-report.html`

## 4. 代码质量修复

- [x] 4.1 局部变量 `html` 重命名为 `html_content`，消除对 `import html` 模块的遮蔽
- [x] 4.2 Response `content=html_content` 引用更新

## 5. 验证

- [x] 5.1 正常仓库 URL 的 Badge SVG 生成无异常
- [x] 5.2 正常仓库的 HTML 导出报告内容完整
- [x] 5.3 修复 P0 Issue #1
