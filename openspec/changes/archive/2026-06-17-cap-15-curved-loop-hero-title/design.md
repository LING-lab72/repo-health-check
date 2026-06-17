## Context

项目前端已完成 React Bits 风格改造：Iridescence WebGL 流动背景、Dock macOS 风格底部导航、毛玻璃卡片体系。但首页标题仍为静态 `<h1>` 渐变文字，在动态背景之上缺乏视觉活力和交互性。

React Bits CurvedLoop 组件使用 SVG `<textPath>` 让文字沿贝塞尔曲线循环滚动，支持拖拽交互改变方向和速度。将其引入首页 Hero 区域可提升首屏视觉冲击力和交互趣味。

所有修改已完成并通过 TypeScript 编译验证，此设计文档记录技术决策。

## Goals / Non-Goals

**Goals:**
- 首页标题从静态文字升级为弧形滚动动画
- 支持拖拽交互（用户可拖拽改变滚动方向）
- 动画风格与 Iridescence 背景、Dock 导航、毛玻璃卡片协调统一
- TypeScript 类型安全

**Non-Goals:**
- 不将 CurvedLoop 应用到其他页面（仅首页 Hero 区域）
- 不修改 CurvedLoop 的核心动画算法
- 不新增外部依赖（仅使用 React 内置 hooks + SVG）

## Decisions

### D1: 替换而非叠加——完全替换静态 `<h1>`

**决策**：将 `<h1 className="hero-title">Repo Health Check</h1>` 完全替换为 `<CurvedLoop marqueeText="Repo ✦ Health ✦ Check ✦" />`，而非在 `<h1>` 之上叠加 CurvedLoop。

**替代方案考虑**：
- ❌ 在 `<h1>` 上叠加 CurvedLoop — 两层标题重叠，视觉混乱，信息重复
- ❌ 仅首页标题区域添加装饰动画、保持 `<h1>` — 半静态半动态，风格割裂
- ✅ 完全替换 — 一致性最佳，弧形文字本身就是标题

### D2: curveAmount=280 而非默认 400

**决策**：使用 `curveAmount=280`（较原版 400 更小的弧度），让曲线更平缓，适配首页 Hero 区域的标题功能（过于弯曲会让文字难以辨认）。

**替代方案考虑**：
- ❌ curveAmount=400（默认值） — 弧度太大，标题文字阅读性差
- ❌ curveAmount=150 — 弧度太小，几乎看不出曲线效果，失去 CurvedLoop 特色
- ✅ curveAmount=280 — 弧度适中，既有曲线动感又保持标题可读性

### D3: marqueeText 使用 ✦ 分隔符而非空格

**决策**：文字内容为 `"Repo ✦ Health ✦ Check ✦"`，使用 ✦（四角星）作为分隔符而非纯空格。

**替代方案考虑**：
- ❌ `"Repo Health Check"`（纯空格） — 滚动时词语之间视觉间隔不明显
- ❌ `"Repo | Health | Check |"`（竖线） — 偏技术风格，与 premium 设计不搭
- ✅ `"Repo ✦ Health ✦ Check ✦"` — ✦ 星号既分隔又装饰，与 accent 发光色呼应

### D4: interactive=true 保持拖拽交互

**决策**：保留 `interactive=true`，用户可以拖拽弧形文字改变滚动方向和速度。

**替代方案考虑**：
- ❌ interactive=false — 丧失交互性，仅做纯动画展示，与项目"互动体验"理念不符
- ✅ interactive=true — 拖拽提供微交互乐趣，用户发现后会觉得有趣

### D5: CSS 去掉 min-height:100vh，仅用于标题区域

**决策**：CurvedLoop.css 去掉原版的 `min-height: 100vh`（原版设计用于全页展示），改为 `margin-bottom: 8px` 紧贴 subtitle。字体从 `6rem` 缩小为 `4.5rem`。

**替代方案考虑**：
- ❌ 保留 min-height:100vh — 首页标题区域会撑满整个视口，下方内容被推到看不见
- ❌ 字体 6rem — 标题区域过于庞大，与输入卡片和其他内容比例失调
- ✅ 去掉 min-height、字体 4.5rem — 标题紧凑有力，与下方内容比例协调

### D6: accent 色填充 + drop-shadow 发光而非 SVG gradient

**决策**：使用 `fill: var(--accent)` + `filter: drop-shadow(...)` 发光效果，而非在 SVG 内定义 linearGradient。

**替代方案考虑**：
- ❌ SVG `<defs><linearGradient>` — textPath 上 gradient 需要额外 SVG 命名空间管理，且组件每次渲染生成唯一 uid，gradient 引用可能不稳定
- ❌ 纯白 fill — 与 Iridescence 流动背景冲突，缺乏品牌色识别
- ✅ accent 色 + drop-shadow — 简单可靠，accent indigo 色 (#818cf8) 与 Iridescence 背景 (紫色调) 协调，drop-shadow 给文字增加发光质感

## Risks / Trade-offs

- **[SVG textPath 渲染兼容性]** → IE 不支持 textPath，但项目已不考虑 IE。现代浏览器（Chrome/Firefox/Safari/Edge）全部支持。
- **[字体大小响应式]** → 原版 CurvedLoop CSS 无响应式。本次新增 768px/480px 响应式断点，但极端小屏（<360px）可能仍显拥挤。
- **[拖拽与页面滚动冲突]** → pointerDown/Move 事件在 CurvedLoop jacket div 上监听，setPointerCapture 确保拖拽不触发页面滚动。但如果用户在移动端触摸滑动，可能偶尔触发拖拽而非滚动——权衡：interactive 提供的趣味性值得这个小风险。
- **[无外部依赖]** → CurvedLoop 仅依赖 React hooks，不引入新 npm 包。但组件代码量较大（约 130 行），维护需理解 SVG textPath + requestAnimationFrame 动画机制。
