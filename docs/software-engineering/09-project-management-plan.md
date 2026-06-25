# 项目管理计划

## 1. 管理目标

项目管理目标是保障 Repo Health Check 在有限课程周期内完成可运行、可演示、可测试、可追踪的开源软件实践项目。

## 2. 过程模型

项目采用迭代式开发与 OpenSpec 规范驱动开发结合：

1. 提出 capability。
2. 编写 proposal/design/tasks/spec。
3. 实现功能。
4. 测试验证。
5. 归档到 `openspec/changes/archive/`。

## 3. 里程碑

| 阶段 | 目标 | 产出 |
| --- | --- | --- |
| M1 项目初始化 | 前后端骨架、OpenSpec 配置 | cap-01 |
| M2 分析引擎 | 六维分析器 | cap-02 |
| M3 报告 API | 分析、Badge、缓存、导出 | cap-03 |
| M4 AI 诊断 | LLM 和本地规则诊断 | cap-04 |
| M5 前端体验 | 高级 UI、雷达图、报告页 | cap-05/cap-16 |
| M6 工程化 | CI/CD、测试、部署、文档 | cap-06/cap-19 |
| M7 产品增强 | PDF、分享卡片、排行榜、PK | cap-20 |
| M8 稳定发布 | 标签、Release、答辩材料 | v2.1.0 |

## 4. 任务拆解

| 类型 | 示例任务 |
| --- | --- |
| 后端 | API、分析器、缓存、存储、安全加固 |
| 前端 | 首页、报告页、对比页、排行榜、About 页 |
| AI | Prompt、结构化输出、本地规则降级 |
| 工程化 | CI、GitLink、脚本、测试、文档 |
| 产品 | 分享卡片、PDF、Badge、PK 海报 |

## 5. 协作规范

分支建议：

```text
feature/*
fix/*
docs/*
release/*
```

提交信息建议：

```text
feat: add report export
fix: prevent badge xss
docs: add software engineering documents
release: stabilize v2.1.0
```

## 6. 配置管理

关键配置：

- `.env.example`：环境变量模板。
- `frontend/.env`：前端 API 地址。
- `.github/workflows/ci.yml`：GitHub CI。
- `devops/gitlink/*.sh`：GitLink DevOps 脚本。
- `openspec/`：规范和能力归档。

## 7. 质量门禁

每次合并前至少满足：

- 代码能启动。
- 前端 lint/test/build 通过。
- 后端测试通过。
- 不破坏稳定 UI。
- 更新对应文档或 OpenSpec 归档。

