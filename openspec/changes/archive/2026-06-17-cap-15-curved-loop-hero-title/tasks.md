## 1. CurvedLoop 组件创建

- [x] 1.1 创建 `CurvedLoop.tsx`：TypeScript 适配版，React Bits CurvedLoop 组件源码移植
- [x] 1.2 组件 Props 接口定义：`marqueeText`, `speed`, `className`, `curveAmount`, `direction`, `interactive`
- [x] 1.3 `useRef` 绑定 `measureRef`、`textPathRef`、`pathRef`（正确类型 `SVGTextElement | null` 等）
- [x] 1.4 `useMemo` 处理 `marqueeText` 结尾空格规范
- [x] 1.5 `useEffect` 计算文字间距（`measureRef.getComputedTextLength()`）
- [x] 1.6 `useEffect` requestAnimationFrame 循环驱动 `startOffset` 动画
- [x] 1.7 拖拽交互：`onPointerDown/Move/Up/Leave` + `setPointerCapture`
- [x] 1.8 `useId()` 生成唯一 `pathId`（支持多实例）

## 2. CurvedLoop CSS 样式

- [x] 2.1 创建 `CurvedLoop.css`：去掉原版 `min-height: 100vh`
- [x] 2.2 `.curved-loop-svg`：字体 4.5rem，accent 色 fill，drop-shadow 发光
- [x] 2.3 响应式：`@media (max-width: 768px)` 字体 2.4rem，`@media (max-width: 480px)` 字体 1.8rem
- [x] 2.4 `.curved-loop-jacket`：`margin-bottom: 8px`，居中布局

## 3. 首页 Hero 区域集成

- [x] 3.1 `HomePage.tsx` 引入 `CurvedLoop` 组件
- [x] 3.2 替换 `<h1 className="hero-title">` 为 `<CurvedLoop>` 组件
- [x] 3.3 配置 props：`marqueeText="Repo ✦ Health ✦ Check ✦"`, `curveAmount=280`, `speed=2`, `direction="left"`, `interactive=true`
- [x] 3.4 `index.css` 新增 `.curved-loop-hero-text` 样式类：`fill: var(--accent)`, `font-family: var(--font-sans)`

## 4. TypeScript 编译验证

- [x] 4.1 `npx tsc --noEmit` 编译通过，无类型错误
