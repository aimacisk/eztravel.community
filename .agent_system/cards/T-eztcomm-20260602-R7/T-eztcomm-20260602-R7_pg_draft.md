---
task_id: T-eztcomm-20260602-R7
title: ProductDetail 路由修復 + seed data
author: pg
wiki_target: 06_wiki/04_dev_guide.md
sections: [routing-fix, seed-data, no-migration]
---

## §R7 ProductDetail 路由修復（T-eztcomm-20260602-R7）

### 根本原因

`ProductController.cs` action attribute 錯誤導致路由偏移：

```
修復前：[HttpGet("detail/{id:int}")]  → /product/detail/1  ← 404
修復後：[HttpGet("{id:int}")]         → /product/1         ← 200 ✅
```

controller 類別上已有 `[Route("product")]`，action 只需 `"{id:int}"`。

### Seed Data 策略（Development）

專案使用 **InMemory DB**（`EnsureCreatedAsync` + runtime seed），無需 EF migration。
種子資料位於 `Program.cs`，開發環境啟動時自動注入 4 筆：

| Id | Name | Category |
|----|------|----------|
| 1 | 日本東京自由行 5 天 4 夜 | FreeTour |
| 2 | 泰國曼谷團體深度旅遊 | GroupTour |
| 3 | 沖繩海濱飯店 3 晚自由行 | Hotel |
| 4 | 環球影城一日票 | **Ticket**（R7 新增）|

**重要**：`Product` entity 沒有 `Price` 欄位，`Category` 是 enum（`ProductCategory`），不是 int `CategoryId`。

### 視覺 Tokens（不需改動）

`wwwroot/css/site.css` 已正確定義：
- `body { background-color: var(--color-bg-primary); }` → `#F1F7F8`（AC-R7-04）
- `.navbar { background-color: var(--color-brand-primary) !important; }` → `#11D073`（AC-R7-05）

### 編譯與驗證

```bash
# admin 執行（git BLOCKED in pg sandbox）
cd projects/eztravel.community/.worktrees/T-eztcomm-20260602-R7
dotnet build eztravel.Community.sln
# 驗證路由
curl http://localhost:5150/product/1  # 期望 HTTP 200
curl http://localhost:5150/product/4  # 期望 HTTP 200
```

### 已知限制

commit_sha=PENDING_ADMIN_COMMIT（sandbox git 指令 BLOCKED）。Admin 需執行 rebase + merge 流程。
