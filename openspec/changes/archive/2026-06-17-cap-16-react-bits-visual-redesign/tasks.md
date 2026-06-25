## 1. Iridescence WebGL 背景组件

- [x] 1.1 创建 `Iridescence.tsx`：基于 ogl 的 WebGL Fragment Shader 流动背景组件
- [x] 1.2 创建 `Iridescence.css`：全屏 fixed 定位 + z-index 层级管理
- [x] 1.3 Shader 代码：Fragment Shader 实现多色流动渐变，支持 color / speed / amplitude 配置
- [x] 1.4 WebGL 可用性检测：不支持时 fallback 为纯色背景
- [x] 1.5 `App.tsx` 集成：`<Iridescence color={[0.33, 0.22, 0.55]} />` 作为全局背景层

## 2. Dock 底部导航组件

- [x] 2.1 创建 `Dock.tsx`：macOS 风格底部 Dock 导航栏
- [x] 2.2 创建 `Dock.css`：底部居中定位 + 毛玻璃背景 + 圆角边框
- [x] 2.3 hover 放大动画：使用 `motion` 库 `useMotionValue` + `useTransform` 实现弹簧放大效果
- [x] 2.4 SVG 图标集成：Home / Chart / Trophy / GitCompare / Info 五枚语义图标
- [x] 2.5 `App.tsx` 替换：用 `<Dock />` 替换原有 `<Navbar />`
- [x] 2.6 `Navbar.tsx` 重写：保留路由逻辑，重构为 Dock 内部组件

## 3. GlassCard 毛玻璃卡片组件

- [x] 3.1 创建 `GlassCard.tsx`：通用毛玻璃卡片容器组件
- [x] 3.2 `backdrop-filter: blur(16px)` + 半透明白色边框 + 渐变背景
- [x] 3.3 Props 接口：`children`, `className`, `style` 透传
- [x] 3.4 暗色/亮色主题自适应（通过 CSS 变量）

## 4. AnimatedCounter 数字计数器

- [x] 4.1 创建 `AnimatedCounter.tsx`：requestAnimationFrame 驱动的数字滚动组件
- [x] 4.2 Props 接口：`value`, `duration`, `easing` 配置
- [x] 4.3 数值从 0 平滑滚动到目标值，支持 easeOutCubic 缓动
- [x] 4.4 组件卸载时清理 animation frame

## 5. BackgroundGlow 发光层组件

- [x] 5.1 创建 `BackgroundGlow.tsx`：CSS radial-gradient 发光层，用于卡片背景点缀
- [x] 5.2 支持 `color` 和 `size` 配置

## 6. 页面重写——全部 5 页面适配毛玻璃卡片布局

- [x] 6.1 `HomePage.tsx`：输入卡片 + 特性介绍卡片使用 GlassCard 包裹
- [x] 6.2 `ReportPage.tsx`：雷达图 + 分数 + AI 诊断 + Badge 代码区域使用 GlassCard
- [x] 6.3 `LeaderboardPage.tsx`：排行榜列表使用 GlassCard
- [x] 6.4 `ComparePage.tsx`：双仓库对比区域使用 GlassCard
- [x] 6.5 `AboutPage.tsx`：项目介绍 + SDD 流程 + 贡献指南使用 GlassCard

## 7. 共享组件暗色主题适配

- [x] 7.1 `RadarChart.tsx`：tooltip 暗色背景 + 雷达图配色调整
- [x] 7.2 `ScoreBar.tsx`：shimmer 动画 + 暗色轨道底色
- [x] 7.3 `index.html`：新增 Fira Code 本地 `@font-face` 声明
- [x] 7.4 `package.json`：新增 `motion@^12.40.0` 和 `ogl@^1.0.11` 依赖
- [x] 7.5 TypeScript 编译验证通过
