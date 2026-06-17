## 1. 后台任务模式

- [x] 1.1 analyze.py: force_sync 参数 + BackgroundTasks + _pending_tasks
- [x] 1.2 GET status 返回 pending/completed/not_found
- [x] 1.3 ReportPage.tsx: code=1 时 3s 轮询 + 5min 超时

## 2. 投票防刷

- [x] 2.1 storage.py: cast_vote 添加 client_ip 参数 + 60s cooldown
- [x] 2.2 vote.py: Request 对象提取 IP + HTTP 429
- [x] 2.3 LeaderboardPage.tsx: 429 错误提示

## 3. 修复

- [x] 3.1 ComparePage 维度匹配改为名称查找
- [x] 3.2 main.py CORS 从 CORS_ORIGINS 环境变量读取
- [x] 3.3 RadarChart/HistoryChart 添加 window resize 自适应

## 4. 验证

- [x] 4.1 tsc 0 错误
- [x] 4.2 pytest 76/76 通过
