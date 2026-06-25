## Why

项目前端原有 UI 基于浅色 Bootstrap 风格（Navbar 顶部导航 + BackgroundGlow 渐变背景），视觉表现力与同类工具站同质化严重，缺乏 premium 感和品牌辨识度。

React Bits 提供一套暗色沉浸式 UI 组件体系（WebGL 着色器背景、macOS 风格 Dock 导航、毛玻璃卡片），已在开源社区得到广泛验证。将其整体引入可一步到位地完成视觉升级，同时保持 React + TypeScript 技术栈不变。

## What Changes

- 替换 `BackgroundGlow` 为 `Iridescence` WebGL 着色器流动背景（基于 ogl + motion）
- 替换顶部 `Navbar` 为 `Dock` macOS 风格底部导航栏（hover 放大 + 弹簧动画）
- 新增 `GlassCard` 毛玻璃卡片组件（backdrop-filter blur + 半透明边框）
- 新增 `AnimatedCounter` 数字滚动计数器组件（requestAnimationFrame 驱动）
- 新增 `BackgroundGlow` 组件（CSS radial-gradient 发光层，用于卡片背景点缀）
- 重写全部 5 个页面（Home / Report / Leaderboard / Compare / About）使用毛玻璃卡片布局
- `RadarChart` / `ScoreBar` 适配暗色主题（tooltip 暗色 + shimmer 动画）
- `index.html` 新增 Fira Code 本地字体声明
- `package.json` 新增 `motion` 和 `ogl` 依赖

## Capabilities

### New Capabilities

- `iridescence-background`：WebGL 着色器流动背景（ogl + motion，紫色调 [0.33, 0.22, 0.55]）
- `dock-navigation`：macOS 风格底部 Dock 导航栏（hover 放大 + 弹簧动画 + SVG 图标）
- `glass-card`：毛玻璃卡片组件（backdrop-filter blur + 半透明边框 + 渐变背景）
- `animated-counter`：数字滚动计数器（requestAnimationFrame 驱动，支持 duration 和 easing）

### Modified Capabilities

- `frontend-real-api`：全部页面从 Bootstrap 浅色风格重写为 React Bits 暗色沉浸风格，组件体系全面替换

## Impact

- **Frontend**: 新增 7 个文件（Iridescence.tsx/css, Dock.tsx/css, GlassCard.tsx, AnimatedCounter.tsx, BackgroundGlow.tsx），修改 8 个文件（App.tsx, Navbar.tsx, RadarChart.tsx, ScoreBar.tsx, 5 个页面组件, index.html, package.json）
- **Backend**: 无影响
- **API**: 无 breaking change
- **Dependencies**: 新增 `motion@^12.40.0`（动画引擎）和 `ogl@^1.0.11`（WebGL 着色器）
