# Repo Health Check

> 一键体检 GitHub 仓库健康度：六维分析、AI 诊断、Badge、排行榜、仓库 PK、报告导出和分享海报。

**中文** | [English](./README_EN.md)

## 功能亮点

- **六维健康分析**：代码质量、测试覆盖、架构健康、文档完整、依赖安全、工程规范。
- **AI 诊断建议**：有 DeepSeek/OpenAI Key 时调用 LLM；无 Key 时自动使用本地规则诊断。
- **缓存感知分析**：30 分钟内刷新报告直接使用缓存，避免重复克隆和长时间等待。
- **可视化报告**：雷达图、维度分数条、语言分布饼图、历史趋势与同类参考线。
- **导出与分享**：HTML 报告、浏览器 PDF 导出、Wrapped 风格分享卡片。
- **仓库 PK Arena**：两个仓库并行分析，用动画血条展示胜负，并生成 PK 海报。
- **排行榜**：SQLite 持久化、分页、投票冷却、趋势标记。
- **安全加固**：HTML/SVG 转义、Session 强密钥、OAuth state 校验、CORS 白名单。
- **工程化**：GitHub Actions、pytest、Vitest、OpenSpec 规范化归档、一键启动脚本。

## 截图预览

### 首页

![首页](docs/screenshots/home.png)

### 分析报告

![分析报告](docs/screenshots/report.png)

### 仓库 PK 对比

![仓库 PK 对比](docs/screenshots/compare.png)

### 排行榜

![排行榜](docs/screenshots/leaderboard.png)

### 关于页

![关于页](docs/screenshots/about.png)

## 快速开始

### 一键启动（推荐）

Windows 用户可以直接双击项目根目录中的：

```text
Start-RepoHealth.bat
```

脚本会启动：

- 后端：`http://127.0.0.1:8002`
- 前端：`http://127.0.0.1:5174`

如果缺少 `.env`，脚本会从 `.env.example` 自动复制；如果前端缺少 `node_modules`，脚本会自动执行 `npm install`。

### 手动启动

环境要求：

- Python 3.11+
- Node.js 20+
- Git

后端：

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002 --reload
```

前端：

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

打开：

```text
http://127.0.0.1:5174
```

## 配置

复制配置模板：

```bash
cp .env.example .env
```

| 变量 | 说明 | 默认/示例 |
| --- | --- | --- |
| `SESSION_SECRET` | Session 签名密钥，生产环境必须设置 | 必填 |
| `CORS_ORIGINS` | 允许访问后端的前端来源 | `http://localhost:5174,http://127.0.0.1:5174,...` |
| `FRONTEND_URL` | OAuth 登录后跳转地址 | `http://localhost:5174` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key，可选 | 空 |
| `OPENAI_API_KEY` | OpenAI API Key，可选 | 空 |
| `GIT_HTTP_PROXY` | Git 克隆代理，可选 | `http://127.0.0.1:7890` |
| `TRUST_PROXY_HEADERS` | 是否信任 `X-Forwarded-For` | `false` |
| `ALLOW_NPX_INSTALL` | 是否允许自动安装 npx 工具 | `0` |

无 API Key 时系统仍会自动生成本地规则诊断；配置 Key 后会升级为 LLM 诊断。

## 项目结构

```text
repo-health-check/
├─ backend/
│  ├─ main.py              # FastAPI 入口
│  ├─ routes/              # analyze, badge, auth, compare, export, history, leaderboard, vote
│  ├─ analyzer/            # 六维分析器
│  ├─ ai/                  # AI/本地规则诊断
│  ├─ services/            # clone, cache, storage, session
│  └─ tests/               # pytest
├─ frontend/
│  ├─ src/pages/           # Home, Report, Leaderboard, Compare, About
│  ├─ src/components/      # RadarChart, ScoreBar, LanguagePieChart 等
│  ├─ src/utils/           # 分享卡片、PDF、PK 海报工具
│  └─ package.json
├─ docs/screenshots/       # README 截图
├─ openspec/               # OpenSpec 规格和 capability 归档
├─ data/                   # SQLite 运行时数据
├─ Start-RepoHealth.bat    # Windows 一键启动脚本
└─ README.md
```

## API 概览

| 路由 | 说明 |
| --- | --- |
| `POST /api/analyze` | 分析仓库，支持缓存命中和异步任务 |
| `GET /api/analyze/status` | 查询异步分析状态 |
| `GET /api/badge/{hash}` | 生成 SVG 健康徽章 |
| `GET /api/export/{hash}` | 导出 HTML 报告，可用于浏览器打印 PDF |
| `POST /api/compare` | 并行分析两个仓库并返回对比结果 |
| `GET /api/leaderboard` | 分页排行榜 |
| `POST /api/vote` | 仓库投票 |
| `GET /api/history/{repo}` | 历史趋势数据 |

## 测试

后端：

```bash
python -m pytest backend/tests
```

前端：

```bash
cd frontend
npm run lint
npm test -- --run
npm run build
```

## OpenSpec 规范化

本项目使用 OpenSpec 管理能力变更：

- `openspec/specs/`：长期维护的能力规格
- `openspec/changes/archive/`：已完成 capability 的 proposal、design、tasks 和规格快照

近期重点 capability：

- `cap-19-security-architecture-hardening`：安全加固、SQLite、CI/CD、Compare 并行化
- `cap-20-report-leaderboard-ux`：缓存感知报告、分页榜单、PDF/HTML 导出、分享卡片、PK Arena

## 贡献

欢迎提交 Issue 和 Pull Request。建议流程：

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

更多说明见：

- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [SECURITY.md](./SECURITY.md)
- [CHANGELOG.md](./CHANGELOG.md)

## License

MIT
