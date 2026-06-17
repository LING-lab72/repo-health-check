## Why

首页 Hero 区域使用静态 `<h1>` 文字标题，与项目整体 React Bits 暗色沉浸风格（Iridescence WebGL 流动背景、Dock 底部导航、毛玻璃卡片）不匹配——标题缺乏动态感和交互性，视觉冲击力不足。

React Bits 的 CurvedLoop 组件提供 SVG textPath 弧形滚动文字动画，支持拖拽交互改变滚动方向，完美契合项目追求的 premium 动态体验。

## What Changes

- 新增 `CurvedLoop.tsx`：React Bits CurvedLoop 组件的 TypeScript 适配版本
- 新增 `CurvedLoop.css`：适配暗色沉浸主题的样式（去掉全页布局，accent 色填充 + drop-shadow 发光）
- `HomePage.tsx`：Hero 区域静态 `<h1>` 标题替换为 `<CurvedLoop>` 弧形动画标题
- `index.css`：新增 `.curved-loop-hero-text` 样式类

## Capabilities

### New Capabilities

- `curved-loop-hero-title`：首页弧形滚动标题动画（SVG textPath + interactive 拖拽）

### Modified Capabilities

- `frontend-real-api`：首页 Hero 区域从静态标题升级为 CurvedLoop 动态组件

## Impact

- **Frontend**: 新增 2 个文件（CurvedLoop.tsx + CurvedLoop.css），修改 2 个文件（HomePage.tsx + index.css）
- **Backend**: 无影响
- **API**: 无 breaking change
- **Dependencies**: 无新增依赖（CurvedLoop 仅依赖 React 内置 hooks + SVG）
