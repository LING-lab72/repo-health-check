# CI/CD 配置说明

Repo Health Check 同时提供 GitHub Actions、GitLink/GitLab 风格 CI、Harness Pipeline 三套配置，便于在 GitHub 仓库和 GitLink 仓库中展示自动化质量管理能力。

## GitHub Actions

配置文件：

- `.github/workflows/ci.yml`
- `.github/workflows/cd.yml`

### CI 触发条件

- push 到 `main` / `master`
- Pull Request
- 手动触发 `workflow_dispatch`

### CI 检查内容

- 后端依赖安装
- `flake8` 后端与脚本静态检查
- `pytest backend/tests -q`
- `scripts/e2e_test.py` 端到端冒烟测试
- 前端 `npm run lint`
- 前端 `npm test -- --run`
- 前端 `npm run build`
- 前后端 Docker 镜像构建验证
- 上传 `e2e_report.json` 和 `frontend/dist` 作为构建产物

### CD 触发条件

- 推送 `v*` tag
- 手动触发 `workflow_dispatch`

### CD 内容

- 构建前端生产包
- 编译检查后端源码
- 打包 release artifacts
- 构建可部署 Docker 镜像
- 可选部署前端到 Vercel

如需启用 Vercel 部署，在 GitHub 仓库中配置：

- Repository variable: `VERCEL_ENABLED=true`
- Secrets: `VERCEL_TOKEN`
- Secrets: `VERCEL_ORG_ID`
- Secrets: `VERCEL_PROJECT_ID`

## GitLink / GitLab 风格 CI

配置文件：

- `.gitlab-ci.yml`
- `devops/gitlink/backend-ci.sh`
- `devops/gitlink/frontend-ci.sh`
- `devops/gitlink/package-release.sh`
- `docs/gitlink-devops-setup.md`

`.gitlab-ci.yml` 采用 GitLab CI 兼容语法，适合在支持 GitLab Runner 或同类流水线语法的平台中运行。GitLink 仓库的 DevOps 构建界面通常需要在网页端手动新建构建任务，因此本项目额外提供 `devops/gitlink/*.sh`，可直接复制到 GitLink DevOps 构建步骤中使用。

GitLink 网页端配置步骤见：

```text
docs/gitlink-devops-setup.md
```

### Pipeline 阶段

- `lint`: 后端 flake8 检查
- `test`: 后端 pytest 与 E2E 冒烟测试
- `build`: 前端 lint、Vitest、生产构建
- `package`: 打包前端 dist 与后端源码交付物

### 产物

- `e2e_report.json`
- `frontend/dist/`
- `release/repo-health-frontend-dist.tar.gz`
- `release/repo-health-backend-source.tar.gz`

## Harness Pipeline

配置文件：

- `harness/pipeline.yaml`

Harness Pipeline 用于展示课程要求中的 Harness / SDD 工程实践。当前包含：

- Python lint
- 后端测试
- 前端 lint + build
- E2E 测试
- 前端/后端部署准备阶段

## 本地验证命令

```bash
cd backend
python -m pytest tests -q
```

```bash
cd frontend
npm run lint
npm test -- --run
npm run build
```
