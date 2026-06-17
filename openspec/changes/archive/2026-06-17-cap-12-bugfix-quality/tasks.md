## 1. Bug 修复

- [x] 1.1 HomePage 移除预请求 POST，避免 code=1 误判
- [x] 1.2 Badge hash 改为 crypto.subtle SHA-256，与后端一致
- [x] 1.3 Export 添加 persistent storage fallback

## 2. API 规范化

- [x] 2.1 Vote POST 从 query 改为 body（VoteRequest model）
- [x] 2.2 前端 vote fetch 同步更新

## 3. 配置

- [x] 3.1 Vercel 部署用 API_BASE 环境变量替代硬编码
- [x] 3.2 所有 fetch 改为 `${API_BASE}/api/...`
- [x] 3.3 Session SECRET 从 SESSION_SECRET 环境变量读取

## 4. 代码质量

- [x] 4.1 flake8 修复：F401/F841/F824/W391 ×20
- [x] 4.2 pytest 77/77 通过
- [x] 4.3 tsc 0 错误
