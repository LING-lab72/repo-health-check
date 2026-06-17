## ADDED Requirements

### Requirement: 分析报告展示

系统 SHALL 在 ReportPage 中调用 POST /api/analyze，展示 ECharts 雷达图、六维分数条、AI 诊断建议、问题列表。

#### Scenario: 分析完成展示

- **WHEN** 从 HomePage 提交 URL 后跳转到 /report/:repoId
- **THEN** 页面显示 loading 状态 → 请求完成后渲染雷达图 + 分数条 + AI 诊断

#### Scenario: 六维分数条

- **WHEN** 分析结果包含 6 个维度的分数
- **THEN** 每个维度显示为带颜色的进度条，低分红色、中等黄色、高分绿色

### Requirement: AI 诊断展示

系统 SHALL 在报告页展示 ai_diagnosis 数组，每条建议显示 severity 标签、estimated_hours、confidence 进度环。

#### Scenario: 建议卡片

- **WHEN** ai_diagnosis 包含 3 条建议
- **THEN** 渲染 3 张卡片，severity 为 high 显示红色、medium 黄色、low 蓝色

### Requirement: Badge 嵌入代码

系统 SHALL 在报告页底部展示 Markdown 嵌入代码 `![health](http://host/api/badge/{hash})`，支持一键复制。

#### Scenario: 复制按钮

- **WHEN** 用户点击 Badge 代码旁的复制按钮
- **THEN** 代码被复制到剪贴板，提示 "已复制"

### Requirement: HomePage 交互

系统 SHALL 在 HomePage 实现 URL 格式校验（前端防无效输入）、提交后 loading 动画、错误 toast。

#### Scenario: URL 校验

- **WHEN** 用户输入 "not-a-url" 并提交
- **THEN** 显示红色边框提示 "请输入有效的 GitHub URL"，不发送请求
