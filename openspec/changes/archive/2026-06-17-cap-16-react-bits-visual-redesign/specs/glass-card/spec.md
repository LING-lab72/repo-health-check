# Glass Card

## Purpose

毛玻璃卡片通用容器组件，提供 backdrop-filter blur + 半透明边框 + 渐变背景。

## Requirements

### Requirement: 毛玻璃视觉效果

系统 SHALL 渲染一个容器卡片，应用 `backdrop-filter: blur(16px)` 模糊效果，半透明白色边框（`border: 1px solid rgba(255,255,255,0.1)`），渐变背景，形成毛玻璃视觉层次。

#### Scenario: 在 Iridescence 背景上
- **WHEN** GlassCard 放置在 Iridescence WebGL 背景之上
- **THEN** 卡片区域呈现背景色彩的模糊折射效果，与背景形成视觉分层

### Requirement: Props 透传

系统 SHALL 支持 `children`、`className`、`style` 三个 Props，允许外部自定义卡片类名和内联样式。

#### Scenario: 组合使用
- **WHEN** 多个 GlassCard 在同一页面使用
- **THEN** 各卡片独立渲染，互不影响，支持通过 className 定制各自样式
