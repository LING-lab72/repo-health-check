# Badge API

## Purpose

生成 shields.io 风格的 SVG Badge，展示仓库健康等级（A/B/C/D），可嵌入 README。

## Requirements

### Requirement: SVG Badge 生成

系统 SHALL 提供 GET /api/badge/{repo_hash} 端点，返回 shields.io 风格 SVG Badge，按健康等级着色。

#### Scenario: A 级 Badge

- **WHEN** GET /api/badge/<repo_hash> 且缓存中该仓库 health_score ≥ 80
- **THEN** 返回 SVG，左侧 "health" 灰色，右侧 "A" brightgreen 色

#### Scenario: D 级 Badge

- **WHEN** GET /api/badge/<repo_hash> 且缓存中该仓库 health_score < 40
- **THEN** 返回 SVG，右侧 "D" red 色

#### Scenario: 未缓存仓库

- **WHEN** GET /api/badge/<repo_hash> 且缓存中无此结果
- **THEN** 返回 SVG，"unknown" lightgrey 色

### Requirement: Badge 颜色映射

系统 SHALL 按以下规则映射颜色：A(brightgreen)/B(yellow)/C(orange)/D(red)/unknown(lightgrey)，色值使用 shields.io 标准。

#### Scenario: 颜色精确匹配

- **WHEN** health_score 对应等级为 B
- **THEN** Badge 右侧色值为 yellow（#dfb317）

### Requirement: Content-Type 头

系统 SHALL 为 Badge 端点返回 `Content-Type: image/svg+xml`。

#### Scenario: 正确 Content-Type

- **WHEN** GET /api/badge/hash
- **THEN** HTTP 响应头 Content-Type 为 image/svg+xml

### Requirement: SVG 输出转义

系统 SHALL 对插入 SVG 模板的动态文本进行 HTML 转义，防止 badge_level、label 或 value 中的特殊字符形成 SVG/HTML 注入。

#### Scenario: 恶意文本转义
- **WHEN** Badge value 包含 `<script>alert(1)</script>`
- **THEN** SVG 输出 SHALL 包含转义后的文本，不包含可执行 `<script>` 标签

### Requirement: 共享 Badge 颜色常量

系统 SHALL 使用统一的 Badge 颜色映射常量，Badge SVG 和导出报告 SHALL 复用同一组 shields.io 色值。
