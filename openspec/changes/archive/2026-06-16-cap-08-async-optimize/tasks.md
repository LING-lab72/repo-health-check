## 1. Async 重构

- [x] 1.1 aggregate() 改为 async，import ai_diagnose 替代 sync_diagnose
- [x] 1.2 analyze.py: result = await aggregate()
- [x] 1.3 compare.py: results[label] = await aggregate()
- [x] 1.4 diagnose.py: 删除 sync_diagnose 函数
- [x] 1.5 test_aggregator.py: asyncio.run(aggregate())
- [x] 1.6 test_ai_diagnose.py: asyncio.run(ai_diagnose())
- [x] 1.7 e2e_test.py: async main() + asyncio.run()

## 2. Compare API 规范化

- [x] 2.1 GET → POST + CompareRequest Pydantic model
- [x] 2.2 ComparePage.tsx: fetch POST + JSON body

## 3. Badge 增强

- [x] 3.1 storage.py: 添加 get_by_url_hash() + hashlib import
- [x] 3.2 badge.py: cache miss → storage fallback

## 4. 部署配置

- [x] 4.1 vercel.json: 添加 SPA fallback 规则

## 5. 验证

- [x] 5.1 pytest 76/76 通过
- [x] 5.2 tsc --noEmit 0 错误
