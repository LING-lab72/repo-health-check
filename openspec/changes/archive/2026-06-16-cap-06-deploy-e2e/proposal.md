## Why

cap-01~05 完成后，项目已具备完整的分析能力、API、AI 诊断和前端 UI。最后一步是配置部署（Vercel 前端 + 后端服务）、完善 Harness CI、用自己的仓库做端到端验证，生成项目 README 和社区运营文案，让项目真正可发布。

## What Changes

- 完善 `harness/pipeline.yaml`，添加 deploy stage（Vercel 前端 + 后端 Docker）
- 创建 `vercel.json` 前端部署配置
- 对自有仓库执行端到端分析测试，验证全链路
- 生成完善的 `README.md`（含 Badge、截图、使用说明）
- 创建一个测试脚本 `scripts/e2e_test.sh` 快速验证

## Capabilities

### New Capabilities
- `deploy-config`: Vercel 前端部署 + Harness CI 完整流水线
- `project-readme`: 项目 README 文档
- `e2e-validation`: 端到端测试验证

### Modified Capabilities
- `harness-ci`: pipeline.yaml 添加 deploy stage

## Impact

- 修改：`harness/pipeline.yaml`
- 新增：`vercel.json`、`README.md`、`scripts/e2e_test.sh`
- 无代码逻辑变更
