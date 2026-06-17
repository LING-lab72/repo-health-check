## ADDED Requirements

### Requirement: 暗色主题

系统 SHALL 使用 CSS 变量实现全局暗色主题，背景深色、卡片浅灰、文字高对比度。

#### Scenario: 主题生效

- **WHEN** 页面加载
- **THEN** body 背景为深色 (#0f172a)，文字为浅色 (#e2e8f0)

### Requirement: 动画过渡

系统 SHALL 为卡片 hover、页面进入、按钮交互添加 CSS transition 和 keyframes 动画。

#### Scenario: 卡片 hover

- **WHEN** 鼠标悬停在分析结果卡片上
- **THEN** 卡片在 0.2s 内上浮 4px，阴影加深

### Requirement: 响应式布局

系统 SHALL 支持移动端适配，主要宽度区域在小屏幕下自适应。

#### Scenario: 移动端

- **WHEN** 视口宽度 < 768px
- **THEN** 卡片和表单宽度 100%，padding 减小
