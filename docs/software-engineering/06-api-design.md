# API 接口设计说明书

## 1. 通用响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

| code | 说明 |
| --- | --- |
| 0 | 成功 |
| 1 | 异步任务处理中 |
| -1 | 失败 |

## 2. POST /api/analyze

启动或获取仓库分析。

请求：

```json
{
  "repo_url": "https://github.com/vuejs/vue",
  "force_sync": false,
  "skip_ai": false,
  "ai_api_key": "optional"
}
```

成功返回：

```json
{
  "code": 0,
  "message": "success (cached)",
  "data": {
    "repo_url": "...",
    "health_score": 85,
    "badge_level": "A",
    "dimensions": [],
    "ai_diagnosis": []
  }
}
```

异步返回：

```json
{
  "code": 1,
  "message": "analyzing",
  "data": {
    "task_id": "abc123",
    "repo_url": "https://github.com/vuejs/vue",
    "status": "pending"
  }
}
```

## 3. GET /api/analyze/status

查询异步分析状态。

参数：

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| task_id | 是 | 任务 ID |
| repo_url | 否 | 仓库 URL，用于精确查询 |

返回状态：
- pending
- completed
- failed
- not_found

## 4. GET /api/badge/{hash}

生成仓库健康度 SVG Badge。

安全要求：
- label/value 必须 HTML 转义。
- 输出 Content-Type 为 SVG。

## 5. GET /api/export/{hash}

导出 HTML 报告。

安全要求：
- 所有动态字段必须 HTML 转义。
- 报告可被浏览器打印为 PDF。

## 6. POST /api/compare

对比两个仓库。

请求：

```json
{
  "repo_a": "https://github.com/vuejs/vue",
  "repo_b": "https://github.com/facebook/react",
  "skip_ai": false
}
```

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "repo_a": {},
    "repo_b": {}
  }
}
```

## 7. GET /api/leaderboard

获取排行榜。

建议参数：

| 参数 | 说明 |
| --- | --- |
| page | 页码 |
| page_size | 每页数量 |

## 8. POST /api/vote

为仓库投票。

请求：

```json
{
  "repo_url": "https://github.com/vuejs/vue"
}
```

限制：
- 应支持冷却时间，防止刷票。

## 9. GET /api/history/{repo}

获取某仓库历史趋势。

响应：

```json
{
  "code": 0,
  "data": [
    {
      "analyzed_at": "2026-06-25T10:00:00",
      "health_score": 82,
      "badge_level": "B"
    }
  ]
}
```

## 10. GET /health

健康检查。

响应：

```json
{
  "status": "ok"
}
```

