# GitLink DevOps 构建配置指南

GitLink 的 DevOps 构建需要在网页端手动创建任务。仓库中的 `.gitlab-ci.yml` 可以作为流水线配置参考，但不会像 GitHub Actions 一样自动出现在 GitLink 的构建列表中。

## 推荐配置方式

进入 GitLink 仓库页面：

```text
https://gitlink.org.cn/LINGQvQ/repo-health-check
```

然后按页面入口操作：

```text
DevOps -> 构建 -> 新建构建 / 新建流水线 / 新建任务
```

不同 GitLink 页面版本按钮名称可能略有差异，核心是进入仓库的 DevOps 构建模块后创建一个新的构建任务。

## 构建任务一：后端 CI

建议名称：

```text
repo-health-backend-ci
```

源码仓库：

```text
LINGQvQ/repo-health-check
```

分支：

```text
master
```

构建环境：

```text
Python 3.11
```

环境变量：

```text
SESSION_SECRET=gitlink-ci-session-secret
```

构建命令：

```bash
sh devops/gitlink/backend-ci.sh
```

等价展开命令：

```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt pytest flake8
flake8 backend scripts --config backend/.flake8 --extend-ignore E501
pytest backend/tests -q
python scripts/e2e_test.py
```

产物：

```text
e2e_report.json
```

## 构建任务二：前端 CI

建议名称：

```text
repo-health-frontend-ci
```

构建环境：

```text
Node.js 20
```

构建命令：

```bash
sh devops/gitlink/frontend-ci.sh
```

等价展开命令：

```bash
cd frontend
npm ci
npm run lint
npm test -- --run
npm run build
```

产物：

```text
frontend/dist
```

## 构建任务三：发布包

如果 GitLink DevOps 支持多步骤流水线，可以把发布包任务放在后端 CI 和前端 CI 之后执行。

建议名称：

```text
repo-health-package-release
```

构建命令：

```bash
sh devops/gitlink/package-release.sh
```

产物：

```text
release/repo-health-frontend-dist.tar.gz
release/repo-health-backend-source.tar.gz
```

## 答辩展示建议

答辩时可以展示这三类证据：

- GitHub Actions 页面：证明 GitHub 仓库已有自动 CI/CD
- GitLink DevOps 构建页面：证明 GitLink 仓库已绑定构建任务
- `docs/cicd.md` 和本文件：证明 CI/CD 配置可复现、可迁移

如果现场 GitLink DevOps 还没跑通，也可以说明：仓库已经提供 GitLink DevOps 构建脚本，网页端只需绑定构建任务即可执行。
