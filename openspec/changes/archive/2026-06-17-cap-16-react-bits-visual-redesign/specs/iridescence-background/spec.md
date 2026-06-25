# Iridescence Background

## Purpose

WebGL 着色器流动背景，基于 ogl + motion 实现全屏沉浸式动态背景层。

## Requirements

### Requirement: WebGL 着色器渲染

系统 SHALL 使用 ogl 库加载 Fragment Shader，在全屏 Canvas 上渲染多色流动渐变背景。默认颜色配置为 `color={[0.33, 0.22, 0.55]}`（紫色调），与项目品牌色和 CurvedLoop accent 色协调。

#### Scenario: 正常渲染
- **WHEN** 浏览器支持 WebGL 2.0
- **THEN** 全屏 fixed 定位 Canvas 渲染流动色彩渐变，z-index 置于最底层（-1），不阻挡页面交互

#### Scenario: WebGL 不可用
- **WHEN** 浏览器不支持 WebGL 或 GPU 不可用
- **THEN** fallback 为纯色背景，不抛出错误

### Requirement: 性能控制

系统 SHALL 通过 `speed` 和 `amplitude` 参数控制动画速度和波形幅度，使用 requestAnimationFrame 驱动，页面不可见时自动暂停。
