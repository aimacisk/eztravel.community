---
task_id: T-eztcomm-20260601-W4-AQ-1
parent_wish: W-eztcomm-20260601-REBUILD
phase: QA
generated_at: 2026-06-01T23:30:00Z
generated_by: qa
wiki_target: 06_wiki/05_qa_report.md
sections:
  - 三閘門狀態
  - TC 執行結果
  - Bug 摘要
  - AC 對照
  - 修復建議
---

# W4 QA 驗收報告 — T-eztcomm-20260601-W4-AQ-1

## 執行摘要

| 項目 | 結果 |
|------|------|
| 驗收任務 | T-eztcomm-20260601-W4-AQ-1 |
| 測試範圍 | TC-01 ~ TC-06（E2E + API curl + Playwright 截圖） |
| 測試工具 | curl 8.14.1 + Playwright 1.60.0 + dotnet test xUnit |
| 服務端口 | 5150（launchSettings.json 覆蓋，非 TC 指定的 5000） |
| 環境 | ASPNETCORE_ENVIRONMENT=Development，PostgreSQL 未啟動 |
| AC-5（本機可運作）| ❌ **未達標** |
| 總 Bug 數 | 6（CRITICAL×1、HIGH×3、MEDIUM×2） |
| TC 全 PASS | 0 / 6 |

---

## 一、三閘門狀態

| 閘門 | 狀態 | 說明 |
|------|------|------|
| **閘門 1：全測試 pass** | ❌ FAIL | TC-01~05 FAIL，TC-06 PARTIAL（核心行為正確但規格路由錯誤）；現有 xUnit Test1 通過但內容為空殼 |
| **閘門 2：靜態掃描 pass** | ⚠️ SKIP | 未執行 linter（無 dotnet analyzer 設定），已知路由衝突 BUG-003 屬靜態可偵測問題 |
| **閘門 3：安全掃描 pass** | ⚠️ SKIP | 未執行 security scanner；BUG-006（API 端點回 302 非 401）屬安全設計問題，建議補 Snyk/Bandit 掃描 |

**結論：三閘門未通過，不放行。**

---

## 二、TC 執行結果（逐條）

### TC-01：首頁可正常載入

| 項目 | 值 |
|------|---|
| 目標 URL | http://localhost:5150/ |
| 預期 HTTP | 200，body 含 eztravel 標題文字，分類導航列可見 |
| 實際 HTTP | **500** |
| 截圖 | `workspace/eztcomm-W4-AQ1-screenshots/TC01_home_500.png` |
| **結果** | ❌ **FAIL** |
| 根因 Bug | BUG-eztcomm-20260601-001（`_LoginPartial.cshtml` 缺失） |
| Stack Trace | `InvalidOperationException: partial view '_LoginPartial' was not found at Views/Shared/_Layout.cshtml:39` |

---

### TC-02：分類頁顯示商品列表

| 項目 | 值 |
|------|---|
| TC 指定 URL | http://localhost:5150/category/flights |
| 實際正確 URL | http://localhost:5150/category/flight（slug 無 s） |
| 預期 HTTP | 200，頁面含至少 1 筆商品卡片 |
| 實際 HTTP（TC 路由）| **404**（slug 不存在） |
| 實際 HTTP（正確路由）| **404**（PageDataLoader 找不到資料，回 NotFound） |
| **結果** | ❌ **FAIL** |
| 根因 Bug | BUG-eztcomm-20260601-002（dev fallback 路徑計算錯誤）；BUG-eztcomm-20260601-005（TC slug 錯誤） |
| 補充說明 | 即使路徑修正，BUG-001（_LoginPartial 缺失）也會讓頁面 500 |

---

### TC-03：商品詳情頁顯示社群區塊

| 項目 | 值 |
|------|---|
| TC 指定 URL | http://localhost:5150/product/1/groups |
| 實際正確 URL | http://localhost:5150/product/detail/1 |
| 預期 HTTP | 200，頁面含 id="community-section" |
| 實際 HTTP（TC 路由）| **404**（路由不存在） |
| 實際 HTTP（正確路由）| **500**（PostgreSQL 未啟動）→ NpgsqlException |
| 社群區塊 id | 實際 HTML 使用 `class="community-module"`，無 `id="community-section"` |
| **結果** | ❌ **FAIL** |
| 根因 Bug | BUG-eztcomm-20260601-004（PostgreSQL 未啟動）；BUG-eztcomm-20260601-005（路由錯誤、id 名稱不符） |

---

### TC-04：已登入使用者可送出留言

| 項目 | 值 |
|------|---|
| TC 指定流程 | POST /account/login → POST /review/create |
| 實際正確路由 | POST /Identity/Account/Login → POST /api/products/{productId}/reviews |
| 預期 HTTP | 200/302（留言送出成功） |
| 實際結果 | 無法測試：PostgreSQL 未啟動；已登入狀態無法建立（Identity DB 不可用） |
| **結果** | ❌ **FAIL**（環境缺失） |
| 根因 Bug | BUG-eztcomm-20260601-004（PostgreSQL）；BUG-eztcomm-20260601-005（路由錯誤） |

---

### TC-05：星等統計 API 可查詢

| 項目 | 值 |
|------|---|
| TC 指定 URL | GET /review/stats?productId=1 |
| 預期 HTTP | 200，body 含 "avg" 或 "average" |
| 實際 HTTP | **404**（endpoint 不存在） |
| **結果** | ❌ **FAIL** |
| 根因 Bug | BUG-eztcomm-20260601-005（`/review/stats` endpoint 未實作，ReviewsController 中無此路由） |
| 補充 | 星等統計可從 `GET /api/products/{productId}/reviews` 計算，但尚未提供獨立 stats API |

---

### TC-06：未登入無法送出留言

| 項目 | 值 |
|------|---|
| TC 指定 URL | POST /review/create（未登入） |
| 實際正確 URL | POST /api/products/1/reviews（未登入） |
| 預期 HTTP | 302 跳轉 /account/login |
| 實際 HTTP（TC 路由）| **404**（路由不存在） |
| 實際 HTTP（正確路由）| **302** → Location: `/Identity/Account/Login?ReturnUrl=...` |
| **結果** | ⚠️ **PARTIAL**（核心安全行為正確，但規格路由錯誤；跳轉後登入頁也因 BUG-001 500） |
| 核心行為評估 | [Authorize] 屬性正確攔截未登入請求 ✓；但整個登入流程因 BUG-001 無法完成 |
| 截圖 | `workspace/eztcomm-W4-AQ1-screenshots/TC06_login_redirect.png` |

---

## 三、Bug 摘要

| Bug ID | 嚴重度 | 標題 | 影響 TC | 根因猜測 |
|--------|--------|------|---------|---------|
| BUG-eztcomm-20260601-001 | 🔴 CRITICAL | `_LoginPartial.cshtml` 缺失 → 全站 500 | TC-01, TC-02 | code |
| BUG-eztcomm-20260601-002 | 🟠 HIGH | PageDataLoader dev 路徑計算錯誤 → 分類 404 | TC-02 | code |
| BUG-eztcomm-20260601-003 | 🟠 HIGH | /health 路由衝突（AmbiguousMatchException） | 無直接 TC | code |
| BUG-eztcomm-20260601-004 | 🟠 HIGH | PostgreSQL 未啟動 → DB 端點全 500 | TC-03, TC-04, TC-05 | spec（環境缺失） |
| BUG-eztcomm-20260601-005 | 🟡 MEDIUM | TC 規格路由與實作不符（5 處） | TC-02~06 | spec |
| BUG-eztcomm-20260601-006 | 🟡 MEDIUM | [ApiController] + [Authorize] 應回 401 非 302 | TC-06（架構建議） | architecture |

---

## 四、AC 對照矩陣

| AC | 內容 | 達標 | 說明 |
|----|------|------|------|
| AC-W4AQ1-01 | TC-01~TC-06 全部 PASS | ❌ | 0/6 PASS（1 PARTIAL） |
| AC-W4AQ1-02 | wiki_draft 含每個 TC PASS/FAIL 判定與截圖路徑 | ✅ | 本報告含完整結果 + 截圖路徑 |
| AC-W4AQ1-03 | W4 AC-5（本機可運作）標記達標 | ❌ | BUG-001/002/004 導致基本功能不可用 |
| AC-W4AQ1-04 | TC-06（未登入跳轉）驗收通過 | ⚠️ | 核心行為正確（[Authorize] 攔截），但路由規格有誤且登入頁 500 |

**W4 AC-5（本機可運作）：❌ 未達標**

---

## 五、修復建議（供 PM 仲裁參考）

### 優先 P0（BUG-001 — CRITICAL，阻塞全站）

**建立 `Views/Shared/_LoginPartial.cshtml`：**

執行 scaffold：
```bash
dotnet aspnet-codegenerator identity -dc AppDbContext --files "Account.Login"
```
或手動建立最小化版本：
```html
@using Microsoft.AspNetCore.Identity
@inject SignInManager<ApplicationUser> SignInManager
@inject UserManager<ApplicationUser> UserManager
<ul class="navbar-nav">
@if (SignInManager.IsSignedIn(User))
{
    <li class="nav-item"><a asp-area="Identity" asp-page="/Account/Logout" class="nav-link">登出</a></li>
}
else
{
    <li class="nav-item"><a asp-area="Identity" asp-page="/Account/Login" class="nav-link">登入</a></li>
    <li class="nav-item"><a asp-area="Identity" asp-page="/Account/Register" class="nav-link">註冊</a></li>
}
</ul>
```
**建議派 PG REWORK**（1-2 小時工作量）。

---

### 優先 P1（BUG-002 — HIGH，分類頁 404）

**修正 PageDataLoader.cs 的 devDataRoot 路徑：**

```csharp
// 錯誤：往上 5 層
var devDataRoot = Path.Combine(_env.ContentRootPath, "..", "..", "..", "..", "..", "data", info.FolderName);

// 修正：往上 3 層（ContentRootPath = eztravel.Community.Web，3層上 = eztravel.community 根）
var devDataRoot = Path.Combine(_env.ContentRootPath, "..", "..", "..", "data", info.FolderName);
```
**建議派 PG REWORK**（30 分鐘工作量）。

---

### 優先 P1（BUG-003 — HIGH，/health 衝突）

**刪除 Program.cs 中重複的 health endpoint：**

```csharp
// 移除這行：
app.MapGet("/health", () => Results.Ok(new { status = "ok", ts = DateTime.UtcNow }));
// 保留 HealthController（[ApiController] [Route("[controller]")]）
```
**建議派 PG REWORK**（10 分鐘工作量）。

---

### 優先 P1（BUG-004 — HIGH，PostgreSQL 環境）

**補充前置條件文件（spec 修正）：**
- 在 README.md / 01_requirements/ 補充：「E2E 測試前必須啟動 PostgreSQL 並執行 `dotnet ef database update`」
- 建議加入 `docker-compose.yml` 簡化本機 DB 環境建立
**建議派 BA/AT 補規格 + 加文件（非 PG 代碼問題）**。

---

### 優先 P2（BUG-005 — MEDIUM，TC 規格修正）

TC 指定路由與實作對照修正表：

| TC | 錯誤規格 | 正確規格 |
|----|---------|---------|
| TC-02 | /category/flights | /category/flight |
| TC-03 route | /product/1/groups | /product/detail/1 |
| TC-03 id | id="community-section" | class="community-module" |
| TC-04 | POST /review/create | POST /api/products/{productId}/reviews |
| TC-05 | GET /review/stats?productId=1 | 端點不存在，需另行實作或移除 TC |
| TC-06 | POST /review/create → /account/login | POST /api/products/{id}/reviews → /Identity/Account/Login |

**建議派 BA 修正 TC 規格（test_cases.json 更新）**。

---

### 優先 P2（BUG-006 — MEDIUM，API 設計建議）

`ReviewsController` 應在 [ApiController] 模式下對未授權請求回傳 **401 Unauthorized**，而非 302 重定向。修正方式：

```csharp
// Program.cs 加入 API 認證策略
builder.Services.ConfigureApplicationCookie(opts => {
    opts.Events.OnRedirectToLogin = ctx => {
        if (ctx.Request.Path.StartsWithSegments("/api")) {
            ctx.Response.StatusCode = 401;
            return Task.CompletedTask;
        }
        ctx.Response.Redirect(ctx.RedirectUri);
        return Task.CompletedTask;
    };
});
```
**建議派 PG REWORK（架構優化）**。

---

## 六、測試工具與方法說明

| 工具 | 用途 | 原因 |
|------|------|------|
| curl 8.14.1 | HTTP 端點驗收、狀態碼確認 | 主要驗收工具（Playwright 可用但 BUG-001 導致頁面 500 無意義渲染） |
| Playwright 1.60.0 | 截圖擷取作為 bug 視覺證據 | 補充 curl 的視覺證明 |
| dotnet test (xUnit) | 現有單元測試執行 | 1 個測試（UnitTest1.Test1 空殼），全 PASS |
| dotnet build | 編譯確認 | 0 錯誤 0 警告 ✅ |

**靜態掃描 / 安全掃描：未執行**（環境未配置 analyzer，建議後續補）

---

## 七、截圖清單

| 截圖路徑 | 說明 |
|---------|------|
| `agents/qa/workspace/eztcomm-W4-AQ1-screenshots/TC01_home_500.png` | TC-01 首頁 500 錯誤頁（_LoginPartial 缺失） |
| `agents/qa/workspace/eztcomm-W4-AQ1-screenshots/TC02_category_flight.png` | TC-02 分類頁空白（404 後空 body） |
| `agents/qa/workspace/eztcomm-W4-AQ1-screenshots/TC03_product_groups.png` | TC-03 /product/1/groups 404 |
| `agents/qa/workspace/eztcomm-W4-AQ1-screenshots/TC06_login_redirect.png` | TC-06 登入頁（_LoginPartial 缺失導致 500） |

---

**結論：W4 AC-5（本機可運作）❌ 未達標。共發現 6 個 bug（CRITICAL×1、HIGH×3、MEDIUM×2），全部 TC 未能通過完整驗收。建議 PM 仲裁根因後派 REWORK 給 PG（BUG-001/002/003/006）及 BA（BUG-004/005）。**

[TASK_DONE]
