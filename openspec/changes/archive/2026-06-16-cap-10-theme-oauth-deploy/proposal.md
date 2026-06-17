## Why

项目功能完善后需要提升用户体验和部署便利性：深色/浅色主题切换、GitHub OAuth 登录、报告分享、Docker 一键部署、PDF 导出。

## What Changes

- CSS 双主题变量 + localStorage 持久化
- GitHub OAuth 登录（itsdangerous session）
- 投票改为 GitHub ID 去重
- 报告分享链接复制
- Docker Compose 一键部署
- HTML 报告导出（可打印为 PDF）

## Capabilities

### New Capabilities
- `theme-toggle`: 深色/浅色切换
- `github-oauth`: GitHub OAuth 登录
- `docker-deploy`: Docker Compose 部署
- `report-export`: HTML 报告导出

### Modified Capabilities
- `vote-system`: GitHub ID 去重
- `frontend-real-api`: 分享按钮 + 导出按钮
