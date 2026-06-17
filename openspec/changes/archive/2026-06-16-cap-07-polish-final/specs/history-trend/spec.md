# History Trend

## Purpose

同一仓库多次分析的健康分数变化趋势折线图。

## Requirements

### Requirement: 历史 API

系统 SHALL 提供 GET /api/history/{repo_url} 返回仓库所有历史分析记录。

### Requirement: 趋势图

前端 SHALL 用 ECharts 折线图展示健康分变化趋势，包含 A/B 等级参考线。
