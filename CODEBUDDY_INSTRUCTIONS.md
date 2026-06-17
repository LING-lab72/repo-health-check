# 🔴 两大关键 Bug 修复指令（CodeBuddy v4）

> 生成时间：2026-06-17 09:41
> 优先级：P0 — 功能性致命 Bug

---

## Bug 1：分析超时

### 根因分析

当前分析流程有 **4 个瓶颈叠加**：

| 瓶颈 | 位置 | 耗时估计 | 原因 |
|------|------|---------|------|
| ① git clone | `clone.py:64` | 10-60s | 大仓库 clone --depth 1 仍然很慢；timeout=60s 太短 |
| ② 6 维度同步分析 | `aggregator.py:76-84` | 30-120s | 6 个 analyzer 逐个跑（串行），每个要遍历文件树 |
| ③ AI 诊断 | `diagnose.py:155` | 5-30s | httpx 请求 LLM API，timeout=30s |
| ④ asyncio.run 在线程池 | `analyze.py:51` | — | `_run_sync_aggregate` 用 `asyncio.run(aggregate())`，但 aggregate 内部的 `await ai_diagnose()` 会创建新事件循环跑异步代码 |

**叠加后果**：小仓库 ~60s，中等仓库 ~180s，大仓库超时。

**前端配合问题**：
- `ReportPage.tsx:64` 发送 `force_sync: false` → 后端走 async 模式 → 返回 `code=1` + task_id
- 前端每 3s 轮询 `analyze/status`（`ReportPage.tsx:99-114`），最多 100 次 = 5 分钟
- 但后端 `_run_analysis` 跑在 `BackgroundTasks` 中，而 `BackgroundTasks` 是在响应完成后才执行的
- **问题**：如果 force_sync 模式下，整个 clone + analyze + AI 都在一个请求内完成，没有超时保护

### 修复指令（3 条）

#### 指令 1：增加 clone 超时 + 添加 FastAPI 请求级超时

```
修改 backend/services/clone.py：
1. 把 CLONE_TIMEOUT 从 60 改为 120（大仓库需要更多时间）
2. 在 clone_repo 函数中，git clone 命令增加 --filter=blob:none 参数（只拉文件树不拉大 blob，大幅加速）

修改 backend/routes/analyze.py：
1. 在 analyze_repo 函数顶部（force_sync 分支内），添加总体超时保护：
   - 用 asyncio.wait_for 包裹整个 force_sync 流程，超时 180s
   - 超时后返回 HTTPException 504 Gateway Timeout

具体代码：
- clone.py 第 11 行：CLONE_TIMEOUT = 120
- clone.py 第 64-65 行，git clone 命令改为：
  ["git", "clone", "--depth", "1", "--filter=blob:none", "--quiet", url, str(dest)]
- analyze.py force_sync 分支（第 96-123 行），用 asyncio.wait_for 包裹：
  try:
      result = await asyncio.wait_for(
          loop.run_in_executor(None, _run_sync_aggregate, repo_path, repo_url),
          timeout=180.0
      )
  except asyncio.TimeoutError:
      shutil.rmtree(repo_path.parent, ignore_errors=True)
      err = _make_error(repo_url, "分析超时（超过 180 秒），仓库可能过大")
      cache.set(repo_url, err)
      return ApiResponse(code=-1, message="timeout", data=err)
```

#### 指令 2：Analyzer 并行化 + 跳过 AI 诊断加速

```
修改 backend/analyzer/aggregator.py：
1. 把 6 个 analyzer 从串行改为并行（用 asyncio + run_in_executor）
2. 如果请求参数 skip_ai=True，跳过 AI 诊断（省 5-30s）

具体代码改动（aggregator.py）：

async def aggregate(repo_path: Path, repo_url: str, skip_ai: bool = False) -> dict[str, Any]:
    import asyncio
    
    loop = asyncio.get_running_loop()
    
    # 并行跑 6 个 analyzer
    tasks = []
    for analyzer in ANALYZERS:
        tasks.append(loop.run_in_executor(None, analyzer.analyze, repo_path))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    dimensions = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            dimensions.append({
                "dimension": getattr(ANALYZERS[i].__class__, "dimension", "unknown"),
                "score": 0.0,
                "details": {"error": str(r)},
                "issues": [f"Analysis failed: {r}"],
            })
        else:
            dimensions.append({
                "dimension": r.dimension,
                "score": r.score,
                "details": r.details,
                "issues": r.issues,
            })

    health_score = _compute_health_score(dimensions)
    badge = _get_badge_level(health_score)

    # AI diagnosis (skip if requested)
    try:
        ai_diagnosis_result = await ai_diagnose(dimensions, repo_url) if not skip_ai else []
    except Exception:
        ai_diagnosis_result = []

    return {
        "repo_url": repo_url,
        "health_score": health_score,
        "badge_level": badge["level"],
        "badge_color": badge["color"],
        "badge_description": badge["description"],
        "dimensions": dimensions,
        "ai_diagnosis": ai_diagnosis_result,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }

同时修改 backend/routes/analyze.py：
1. AnalyzeRequest 增加 skip_ai: bool = Field(default=False)
2. _run_sync_aggregate 传入 skip_ai 参数
3. 注意：_run_sync_aggregate 用 asyncio.run()，但 aggregate 内部用了 asyncio.gather，
   asyncio.run 会创建新事件循环，这没问题，因为是在线程中执行的
4. force_sync 分支中的 loop.run_in_executor 也传入 skip_ai

修改前端 ReportPage.tsx 第 64 行：
- 把 force_sync: false 改为 force_sync: true（等待分析完成再返回，避免轮询复杂性）
- 同时添加 skip_ai: true 作为默认（首次分析跳过 AI 诊断加速，用户可在报告页点"获取 AI 诊断"按钮单独请求）
```

#### 指令 3：前端超时体验优化

```
修改 frontend/src/pages/ReportPage.tsx：

1. 改用 force_sync: true 模式（不再走 async 轮询），但增加前端 fetch 超时：
   - 在 fetch 调用增加 AbortController + setTimeout(180000) 即 3 分钟超时
   
   具体代码（替换第 58-83 行的整个 try-catch）：
   const controller = new AbortController();
   const timeoutId = setTimeout(() => controller.abort(), 180000); // 3min
   
   try {
     const resp = await fetch(endpoint, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       signal: controller.signal,
       body: isLocal
         ? undefined
         : JSON.stringify({ repo_url: repoUrl, force_sync: true, skip_ai: true }),
     });
     clearTimeout(timeoutId);
     const json = await resp.json();
     // ... 原有的 code === 0 / -1 处理逻辑保持不变
   } catch (err) {
     clearTimeout(timeoutId);
     if (err instanceof DOMException && err.name === 'AbortError') {
       dispatch({ type: 'ANALYSIS_ERROR', payload: '分析超时（超过 3 分钟），仓库可能过大，请尝试较小的仓库' });
     } else {
       dispatch({ type: 'ANALYSIS_ERROR', payload: '无法连接后端服务' });
     }
   }

2. 移除 async 轮询相关的 useEffect（第 91-117 行的整个 polling useEffect），因为不再需要

3. 移除 taskId 和 pollCount 相关的 state 和逻辑（第 29-30 行、第 37-41 行的 reset useEffect）

4. 在 loading 界面中（第 152-166 行），移除"后台处理中"提示，改为显示更友好的等待信息：
   <p style={{ marginTop: 16, color: 'var(--text-secondary)' }}>
     正在克隆并分析 {displayRepo}，通常需要 30-120 秒...
   </p>

5. 在分析成功后，添加一个"获取 AI 诊断"按钮（当 ai_diagnosis 为空时）：
   {diagnosis.length === 0 && (
     <div className="card" style={{ marginBottom: 24 }}>
       <h2 className="section-title">AI 诊断建议</h2>
       <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 12 }}>
         首次分析跳过了 AI 诊断以加速结果，点击按钮获取：
       </p>
       <button 
         className="btn btn-primary"
         onClick={handleFetchDiagnosis}
       >
         🤖 获取 AI 诊断
       </button>
       {aiLoading && <div className="spinner" style={{ marginTop: 12 }} />}
     </div>
   )}

6. 新增 handleFetchDiagnosis 函数和 aiLoading state：
   const [aiLoading, setAiLoading] = useState(false);
   
   const handleFetchDiagnosis = async () => {
     setAiLoading(true);
     try {
       const resp = await fetch(`${API_BASE}/api/analyze`, {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ repo_url: repoUrl, force_sync: true, skip_ai: false }),
       });
       const json = await resp.json();
       if (json.code === 0 && json.data) {
         dispatch({ type: 'ANALYSIS_SUCCESS', payload: json.data });
       }
     } catch {
       // 静默失败，保持当前结果
     }
     setAiLoading(false);
   };

7. 新增 /api/analyze/local 也需要支持 skip_ai 参数（可选优化）：
   - 修改 analyze.py 的 analyze_local 函数，接受 skip_ai query param
```

---

## Bug 2：缓存污染（自检后所有仓库都显示相同结果）

### 根因分析

**问题流程**：
1. 用户点击"自检本项目" → 调用 `/api/analyze/local`
2. 后端执行分析，把结果用 `cache.set(repo_url, result)` 存入缓存（key = `https://github.com/user/repo-health-check`）
3. 用户再输入其他仓库 URL（如 `https://github.com/psf/requests`）
4. 前端发送 POST `/api/analyze`，`force_sync: false`
5. 后端 async 模式返回 `code=1` + task_id → 前端进入轮询
6. **轮询时**：前端用 `analyze/status?task_id=xxx` 查状态
7. `cache.get_by_hash(task_id)` 遍历缓存中所有 key，**找到第一个匹配 hash 的就返回**
8. 但此时自检的缓存 key 还在内存中！如果新仓库的分析还没完成，**hash 匹配可能碰巧返回了自检的旧结果**

**更致命的 Bug 在前端**：
- `ReportPage.tsx` 的 `useEffect` 用 `fetchStartedRef` 防重复触发
- 但当用户从 `/report/local` 导航到 `/report/https://github.com/psf/requests` 时：
  - `repoId` 变了 → reset useEffect 执行 → `fetchStartedRef.current = false`
  - 主 useEffect 触发 → `state.status === 'success'`（因为自检结果还在 state 里）
  - **第 47 行**：`if (state.status === 'success' || state.status === 'error') return;`
  - **直接跳过了！** 因为自检成功后 state.status 还是 'success'
  - 前端直接渲染了旧的自检数据，只是 URL 标题换了

**这就是为什么"名字改了但数据一样"** — 前端没有在切换仓库时 RESET state。

### 修复指令（2 条）

#### 指令 4：前端切换仓库时 RESET state

```
修改 frontend/src/pages/ReportPage.tsx：

1. 在 reset useEffect（第 37-41 行）中，增加 dispatch RESET：
   useEffect(() => {
     fetchStartedRef.current = false;
     setTaskId(null);
     setPollCount(0);
     dispatch({ type: 'RESET' });  // ← 关键！切换仓库时清除旧结果
   }, [repoUrl]);

2. 这样当 repoUrl 变化时：
   - state.status 回到 'idle'
   - state.analysisResult 被清空
   - 主 useEffect 的 `state.status === 'success'` 检查不再生效
   - 新的分析请求会被正常发起
```

#### 指令 5：后端缓存隔离 + cache key 规范化

```
修改 backend/routes/analyze.py：

1. 在 /api/analyze 和 /api/analyze/local 中，把 cache key 从 repo_url 改为更规范的格式：
   - 统一用 cache.url_hash(repo_url) 作为内部查找 key
   - 或者更好：cache.get() 和 cache.set() 的 key 都用 normalize 后的 URL

2. 更关键的是：在 /api/analyze 的 force_sync 分支开始时，先检查缓存。
   当前逻辑已经有 cache.get(repo_url) 检查（第 88-92 行），这没问题。
   但问题是 /api/analyze/local 用的 URL 是 `https://github.com/user/repo-health-check`，
   这不是用户真正输入的 URL，所以不会冲突。
   
   真正的问题在 cache.get_by_hash() — 它遍历所有缓存条目找 hash 匹配。
   如果两个不同 URL 碰巧 hash 前缀相同（unlikely but possible），会返回错误结果。

3. 修复方案：在 cache.get_by_hash 中，找到匹配后额外验证 repo_url：
   
   修改 backend/services/cache.py 第 76-82 行：
   def get_by_hash(self, repo_hash: str) -> dict[str, Any] | None:
       """Look up cached result by URL hash."""
       with self._lock:
           for url, (result, timestamp) in self._cache.items():
               if self.url_hash(url) == repo_hash and time.time() - timestamp <= self._ttl:
                   # Return a copy with the original URL preserved
                   return dict(result)
       return None
   
   这里其实没问题 — hash 碰撞概率极低。但为安全起见，可以改为只精确查找：

   修改 backend/routes/analyze.py 的 status 接口（第 184-211 行）：
   - 让前端轮询时传递原始 repo_url 而不只是 task_id
   - 在 analyze_repo 返回 code=1 时，data 中同时包含 repo_url
   
   但更简单的修复是：前端不再走 async 轮询模式（指令 3 已改为 force_sync: true），
   所以这个 Bug 自然消失。如果保留 async 模式，需要修改前端传递 repo_url。
```

---

## 📋 修复优先级总结

| 指令 | 修复 | 预估时间 | 依赖 |
|------|------|---------|------|
| #4 | 前端 RESET state（缓存污染根因） | 5 分钟 | 无，最优先 |
| #1 | clone 超时 + git 参数优化 | 10 分钟 | 无 |
| #2 | Analyzer 并行化 + skip_ai | 15 分钟 | 需要测试 |
| #3 | 前端 force_sync + AbortController + AI 按钮 | 20 分钟 | 依赖 #2 |

**建议顺序**：先做 #4（5 分钟搞定缓存污染），再做 #1（超时基础修复），然后 #2 + #3（体验优化）。

做完 #4 后可以立即验证：自检后再输入其他仓库，应该能看到不同的数据。