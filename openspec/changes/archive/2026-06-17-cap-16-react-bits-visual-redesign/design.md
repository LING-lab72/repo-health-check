## Context

项目前端已完成 cap-15 CurvedLoop 弧形标题集成，整体 UI 仍为浅色 Bootstrap + BackgroundGlow 渐变背景。为实现完整的暗色沉浸式体验，需要一次性引入 React Bits 组件体系（Iridescence WebGL 背景、Dock 底部导航、毛玻璃卡片），并重写全部页面组件。

所有修改已完成并通过 TypeScript 编译验证，此设计文档记录技术决策。

## Goals / Non-Goals

**Goals:**
- 从浅色 Bootstrap 风格一步升级为暗色沉浸式 React Bits 体系
- 保持 React 18 + TypeScript 技术栈不变
- 保持所有页面功能不变（路由、API 调用、数据展示逻辑）
- 新增 4 个核心视觉组件（Iridescence / Dock / GlassCard / AnimatedCounter）
- 全部页面使用毛玻璃卡片统一布局

**Non-Goals:**
- 不修改后端 API 或数据格式
- 不新增页面或路由
- 不修改 CurvedLoop 标题组件（已在 cap-15 集成）
- 不引入服务端渲染或 SSG

## Decisions

### D1: Iridescence WebGL 着色器背景替代 BackgroundGlow

**决策**：使用基于 ogl 的 WebGL Fragment Shader 实现流动色彩背景，颜色配置 `color={[0.33, 0.22, 0.55]}`（紫色调），替代原有 CSS radial-gradient BackgroundGlow。

**替代方案考虑**：
- ❌ 保留 BackgroundGlow（CSS gradient） — 静态渐变缺乏动态感，与 CurvedLoop 动画标题风格不搭
- ❌ Three.js 全屏场景 — 过于重量（~600KB），仅用于背景着色器浪费资源
- ✅ ogl + motion — ogl 仅 ~6KB，专为 WebGL 着色器设计；motion 提供声明式动画集成；紫色调与 CurvedLoop accent 色协调

### D2: Dock 底部导航替代 Navbar 顶部导航

**决策**：将顶部 Navbar 完全替换为底部 Dock（macOS 风格），使用 `motion` 库实现 hover 放大弹簧动画。

**替代方案考虑**：
- ❌ 保留顶部 Navbar + 暗色主题 — 顶部导航与沉浸式全屏背景冲突，破坏首屏视觉一体感
- ❌ 侧边栏导航 — 移动端适配复杂，且与"工具站"产品形态不符
- ✅ 底部 Dock — macOS 用户熟悉的交互模式，hover 放大动画增加趣味性，底部位置不遮挡顶部标题区域

### D3: GlassCard 统一卡片体系

**决策**：所有页面内容区域使用 GlassCard 组件包裹——`backdrop-filter: blur(16px)` + 半透明白色边框 + 渐变背景，形成统一的毛玻璃视觉层次。

**替代方案考虑**：
- ❌ 纯色暗色卡片 — 与 WebGL 流动背景搭配时层次感不足
- ❌ 各页面自定义卡片样式 — 风格不统一，维护成本高
- ✅ 统一 GlassCard — 毛玻璃效果在流动背景上形成视觉分层，组件复用降低维护成本

### D4: AnimatedCounter 数字动画

**决策**：分数展示使用 AnimatedCounter 组件（requestAnimationFrame 驱动），从 0 滚动到目标值，给用户"分析正在完成"的即时反馈感。

**替代方案考虑**：
- ❌ 直接显示静态数字 — 缺乏"计算完成"的动态反馈
- ❌ CSS @keyframes 动画 — 无法精确控制终止值和 easing
- ✅ requestAnimationFrame — 精确控制起止值和动画曲线，支持 duration 配置

### D5: 新增 motion + ogl 依赖而非自研

**决策**：引入 `motion@^12.40.0`（Dock 弹簧动画）和 `ogl@^1.0.11`（WebGL 着色器渲染）。

**替代方案考虑**：
- ❌ 自研弹簧动画 — 实现复杂（需物理模拟），且质量难以达到 react-spring/motion 级别
- ❌ 自研 WebGL 着色器框架 — 需要处理 shader 编译、attribute buffer 等底层细节
- ✅ 引入成熟库 — motion 和 ogl 均为轻量级专用库，API 简洁，社区活跃

## Risks / Trade-offs

- **[WebGL 兼容性]** → Iridescence 依赖 WebGL 2.0，极少数设备（如部分低配 Android）可能不支持。缓解：Iridescence 组件内含 WebGL 可用性检测，不支持时 fallback 为纯色背景。
- **[包体积增长]** → motion + ogl 新增约 ~50KB gzip。权衡：视觉升级带来的用户体验提升远超 50KB 加载成本。
- **[Dock 导航学习成本]** → 底部 Dock 与常规 Web 导航模式不同，部分用户可能不习惯。缓解：Dock 图标使用通用语义图标（Home / Chart / Trophy / GitCompare / Info），hover tooltip 显示页面名称。
- **[页面重写工作量大]** → 5 个页面 + 3 个共享组件全部重写。缓解：保持 API 调用和数据流逻辑不变，仅替换 JSX 和样式层。
