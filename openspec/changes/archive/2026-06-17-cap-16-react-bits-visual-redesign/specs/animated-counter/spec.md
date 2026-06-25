# Animated Counter

## Purpose

数字滚动计数器组件，使用 requestAnimationFrame 驱动数值从起始值平滑滚动到目标值。

## Requirements

### Requirement: 数值滚动动画

系统 SHALL 在组件挂载或 `value` prop 变化时，使用 requestAnimationFrame 驱动数值从 0 平滑滚动到目标值，支持配置 `duration`（动画时长）和 `easing`（缓动函数）。

#### Scenario: 默认动画
- **WHEN** 组件挂载，`value=82`
- **THEN** 数字从 0 平滑递增到 82，默认使用 easeOutCubic 缓动曲线（先快后慢）

#### Scenario: 值变化重新动画
- **WHEN** `value` prop 从 82 变为 95
- **THEN** 数字从 0 重新滚动到 95

### Requirement: 资源清理

系统 SHALL 在组件卸载时取消 requestAnimationFrame，防止内存泄漏。

#### Scenario: 组件卸载
- **WHEN** AnimatedCounter 组件从 DOM 中移除
- **THEN** 正在进行的 animation frame 被 cancelAnimationFrame 取消
