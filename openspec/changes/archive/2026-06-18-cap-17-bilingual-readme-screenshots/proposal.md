## Why

项目 README 仅有中文版本，缺少英文版，限制了非中文用户的可访问性。同时 README 缺少截图预览，潜在用户在 clone 代码前无法直观了解界面效果，降低了项目的吸引力和 star 转化率。

开源社区最佳实践要求：双语 README + 截图/GIF 预览 + 顶部语言切换链接，这是提升项目专业度和国际化形象的必要步骤。

## What Changes

- `README.md`：新增截图预览区域（5 张页面截图：首页 / 报告 / 排行榜 / 对比 / 关于），更新 OpenSpec 能力表（cap-15），修正 git clone URL，新增语言切换链接
- `README_EN.md`：新增完整英文版 README（特性、截图、快速开始、评分维度、项目结构、技术栈、网络与缓存、OpenSpec 规范化、测试、贡献指南）
- `docs/screenshots/`：新增 5 张页面截图 PNG（home / report / leaderboard / compare / about）

## Capabilities

### New Capabilities

- 无（纯文档变更，不涉及代码功能）

### Modified Capabilities

- 无（README 变更不影响已归档的 capability spec）

## Impact

- **Frontend**: 无影响
- **Backend**: 无影响
- **API**: 无影响
- **Docs**: 新增 `README_EN.md`（228 行），更新 `README.md`（+33 行截图区域 + 语言切换链接 + cap-15 能力表），新增 5 张截图 PNG 到 `docs/screenshots/`
- **Dependencies**: 无
