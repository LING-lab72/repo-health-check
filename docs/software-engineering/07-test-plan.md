# 测试计划与测试用例

## 1. 测试目标

验证 Repo Health Check 在主要功能、异常场景、安全边界、前端交互和工程化流程中的正确性和稳定性。

## 2. 测试范围

| 范围 | 内容 |
| --- | --- |
| 后端单元测试 | 分析器、缓存、导出、Badge、API、排行榜 |
| 前端单元测试 | 核心组件、Context、键盘可访问性 |
| 集成测试 | 前后端 API 串联、分析流程 |
| E2E 测试 | 本地自分析、健康检查、报告生成 |
| 安全测试 | XSS 转义、Session 密钥、CORS |
| CI 测试 | GitHub Actions / GitLink DevOps |

## 3. 测试环境

| 项目 | 配置 |
| --- | --- |
| 操作系统 | Windows 10/11 或 Linux |
| Python | 3.11+ |
| Node.js | 20+ |
| 后端 | FastAPI + uvicorn |
| 前端 | Vite dev server |
| 数据库 | SQLite |

## 4. 测试命令

后端：

```bash
python -m pytest backend/tests -q
python scripts/e2e_test.py
```

前端：

```bash
cd frontend
npm run lint
npm test -- --run
npm run build
```

## 5. 功能测试用例

| 编号 | 用例 | 步骤 | 预期 |
| --- | --- | --- | --- |
| TC-FR-01 | 首页输入合法仓库 | 输入 `https://github.com/vuejs/vue` 并提交 | 跳转报告页并开始分析 |
| TC-FR-02 | 首页输入非法 URL | 输入普通字符串 | 显示输入错误 |
| TC-FR-03 | 报告生成 | 等待分析完成 | 展示总分、雷达图、AI 建议 |
| TC-FR-04 | 缓存命中 | 短时间再次打开同仓库报告 | 快速返回缓存结果 |
| TC-FR-05 | Badge 复制 | 点击复制 Badge | 剪贴板写入 Markdown |
| TC-FR-06 | HTML 导出 | 点击导出报告 | 下载 HTML 文件 |
| TC-FR-07 | PDF 导出 | 点击导出 PDF | 打开打印窗口 |
| TC-FR-08 | 分享卡片 | 点击生成分享卡片 | 下载 PNG |
| TC-FR-09 | 对比不同仓库 | 输入 A/B 两个仓库 | 展示 A / VS / B 对比 |
| TC-FR-10 | 对比相同仓库 | A/B 输入相同 URL | 显示错误提示 |
| TC-FR-11 | 排行榜投票 | 点击投票按钮 | 投票数增加或进入冷却提示 |
| TC-FR-12 | About 页面 | 打开 `/about` | 展示 cap-01 到 cap-20 |

## 6. 安全测试用例

| 编号 | 场景 | 输入 | 预期 |
| --- | --- | --- | --- |
| TC-SEC-01 | Badge XSS | label/value 包含 `<script>` | SVG 中被转义 |
| TC-SEC-02 | HTML 导出 XSS | advice 包含 HTML 标签 | 导出报告中被转义 |
| TC-SEC-03 | Session 密钥缺失 | 不配置 SESSION_SECRET | 服务拒绝生产启动 |
| TC-SEC-04 | CORS | 非白名单来源请求 | 被拒绝 |
| TC-SEC-05 | OAuth state | 缺失或错误 state | 登录失败 |

## 7. 性能测试用例

| 编号 | 场景 | 指标 |
| --- | --- | --- |
| TC-PERF-01 | 缓存命中 | 1 秒内返回 |
| TC-PERF-02 | 中小型仓库分析 | 180 秒内完成 |
| TC-PERF-03 | Compare 并行分析 | 耗时接近单仓库较慢者，而非两者相加 |

## 8. 回归测试清单

每次发布前必须验证：

- 首页高级 UI 未退化。
- 报告页导出和 AI 诊断正常。
- Compare A / VS / B 布局正常。
- About cap 数量正确。
- `npm run lint` 通过。
- `npm test -- --run` 通过。
- `npm run build` 通过。
- 后端 pytest 通过。

