## Context

项目已完整实现分析、API、AI、前端四大模块，需要完成部署配置和文档化，使其可对外发布。

## Goals / Non-Goals

**Goals:** Vercel 前端部署配置 / Harness CI 完整流水线 / README / e2e 测试脚本 / 自有仓库自测验证

**Non-Goals:** 不配置后端托管（留待后续）

## Decisions

- **Vercel**：前端 SPA 部署，proxy API 到后端
- **Harness**：lint → test → build → e2e → deploy 五阶段
- **e2e**：Python 脚本直接调用 aggregator + diagnose，不依赖 HTTP server

## Risks

- Vercel proxy 需后端服务先启动 → 文档说明部署顺序
