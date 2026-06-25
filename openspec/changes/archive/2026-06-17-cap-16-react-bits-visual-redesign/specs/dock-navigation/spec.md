# Dock Navigation

## Purpose

macOS 风格底部 Dock 导航栏，使用 motion 库实现 hover 放大弹簧动画。

## Requirements

### Requirement: Dock 布局

系统 SHALL 在页面底部居中显示 Dock 导航栏，包含 5 个导航项（首页 / 报告 / 排行榜 / 对比 / 关于），使用 SVG 语义图标，毛玻璃背景 + 圆角边框。

#### Scenario: 导航项点击
- **WHEN** 用户点击 Dock 中的导航图标
- **THEN** 路由切换到对应页面，当前页面图标高亮显示

### Requirement: Hover 弹簧放大动画

系统 SHALL 在用户 hover Dock 图标时，使用 motion 库 `useMotionValue` + `useTransform` 实现弹簧放大效果——hover 图标放大，邻近图标联动放大形成波浪效果，鼠标离开后恢复原位。

#### Scenario: 单个图标 hover
- **WHEN** 用户鼠标 hover 某个 Dock 图标
- **THEN** 该图标平滑放大（约 1.5x），邻近 1-2 个图标联动放大（约 1.2x），形成波浪曲线

#### Scenario: 鼠标离开
- **WHEN** 鼠标离开 Dock 区域
- **THEN** 所有图标平滑恢复到原始大小
