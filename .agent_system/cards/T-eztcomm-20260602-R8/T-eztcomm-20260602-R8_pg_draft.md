---
task_id: T-eztcomm-20260602-R8
agent: pg
type: wiki_draft
wiki_target: 06_wiki/04_dev_guide.md
created_at: 2026-06-02T07:30:00+00:00
---

# T-eztcomm-20260602-R8 — Error.cshtml 套 site.css + StatusCodePages 對接

## 模組結構

```
eztravel.Community.Web/
├── Program.cs                          ← 新增 UseStatusCodePagesWithReExecute
├── Controllers/
│   └── ErrorController.cs             ← 新建：攔截 /Error/{statusCode}
└── Views/Shared/
    └── Error.cshtml                   ← 改寫：套用 _Layout.cshtml + CSS variables
```

### 職責分層

| 檔案 | 變更類型 | 職責 |
|------|---------|------|
| `Program.cs` | 修改 | 加 `UseStatusCodePagesWithReExecute("/Error/{0}")` middleware |
| `ErrorController.cs` | 新建 | 路由 `/Error/{statusCode:int}` → `ViewData["StatusCode"]` → `View("Error")` |
| `Views/Shared/Error.cshtml` | 改寫 | 套 `_Layout.cshtml`（有 site.css + Navbar）+ 中文友善訊息 + 翠綠返回首頁 CTA |

---

## Middleware Pipeline 異動

### 加入前（主要 4xx 狀態）

```
GET /nonexistent-test
→ UseRouting: 無匹配路由
→ 204/404 空白回應（Chrome 顯示預設 404 錯誤頁）
```

### 加入後

```
GET /nonexistent-test
→ UseRouting: 無匹配路由 → 404 狀態
→ UseStatusCodePagesWithReExecute("/Error/404") 攔截
→ 內部重新執行 GET /Error/404
→ ErrorController.Index(statusCode=404)
→ Error.cshtml（套 _Layout.cshtml，顯示友善訊息 + 返回首頁按鈕）
→ Response 回傳 HTTP 404 + HTML body（瀏覽器顯示 app 自有頁）
```

### Program.cs 插入位置

```csharp
app.UseSerilogRequestLogging();

// 自訂錯誤頁：攔截 4xx/5xx 狀態碼，顯示 app 自有錯誤頁（T-eztcomm-20260602-R8）
app.UseStatusCodePagesWithReExecute("/Error/{0}");

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
```

> **注意**：`UseStatusCodePagesWithReExecute` 必須在 `MapControllerRoute` 之前，
> 才能讓 `/Error/{statusCode}` 路由被正確解析。

---

## ErrorController.cs

```csharp
[Route("Error/{statusCode:int}")]
public class ErrorController : Controller
{
    [HttpGet]
    public IActionResult Index(int statusCode)
    {
        ViewData["StatusCode"] = statusCode;
        return View("Error"); // → Views/Shared/Error.cshtml
    }
}
```

**View 解析路徑**（MVC 慣例）：
1. `Views/Error/Error.cshtml` — 不存在
2. `Views/Shared/Error.cshtml` ← 找到，使用此檔 ✅

---

## Error.cshtml 設計

### CSS Token 對應（使用 R1 site.css 實際 token 名稱）

| 用途 | CSS Token | 值 |
|------|-----------|-----|
| 狀態碼大數字顏色 | `--color-text-muted` | `#9BABB8`（淡灰）|
| 標題文字顏色 | `--color-text-primary` | `#1A2B3C`（深色）|
| 說明文字顏色 | `--color-text-secondary` | `#5A7184`（次要）|
| 返回首頁按鈕背景 | `--color-brand-primary` | `#11D073`（翠綠）|
| 按鈕圓角 | `--radius-md` | `8px` |
| 按鈕上下 padding | `--spacing-3` | `12px` |
| 按鈕左右 padding | `--spacing-8` | `32px` |

### 404 / 非 404 分流邏輯

```razor
var code = ViewData["StatusCode"] as int? ?? 0;

@(code == 404 ? "找不到頁面！" : "伺服器發生錯誤")
@(code == 404
    ? "您訪問的頁面不存在，請確認網址是否正確。"
    : "伺服器發生錯誤，請稍後再試。如問題持續，請聯絡客服。")
```

### 與既有 HomeController.Error() 相容性

`HomeController.Error()` 在 production 仍可繼續使用（`UseExceptionHandler("/Home/Error")`）：
- 呼叫 `return View(new ErrorViewModel {...})`
- 新 Error.cshtml 無 `@model` 宣告，接受任意 model（Razor dynamic）
- 不引用 `Model` 屬性，不影響渲染
- `ViewData["StatusCode"]` 未由 HomeController 設定 → 預設 `0` → 顯示「伺服器發生錯誤」✅

---

## 環境配置

- **Runtime**：.NET 8 / ASP.NET Core 8 MVC
- **Worktree**：`.worktrees/T-eztcomm-20260602-R8/`，branch `feat/T-eztcomm-20260602-R8`
- **測試 URL**：`http://localhost:5150/nonexistent-test`（任意不存在路徑）

---

## 編譯與測試（admin 執行）

```bash
# 切入 worktree
cd .worktrees/T-eztcomm-20260602-R8/04_src/eztravel.Community

# 建置
dotnet build eztravel.Community.Web/eztravel.Community.Web.csproj

# 啟動
dotnet run --project eztravel.Community.Web/eztravel.Community.Web.csproj
# → http://localhost:5150

# AC-R8-01: curl 回 404
curl -o /dev/null -w '%{http_code}' http://localhost:5150/nonexistent-test
# 預期輸出: 404

# AC-R8-02~05: Playwright
# browser_navigate http://localhost:5150/nonexistent-test
# browser_evaluate "getComputedStyle(document.body).backgroundColor"
# → 預期含 '241, 247, 248'
# browser_evaluate "getComputedStyle(document.querySelector('.navbar')).backgroundColor"
# → 預期含 '17, 208, 115'
# browser_snapshot → 確認含「找不到頁面」+ 返回首頁按鈕
```

---

## AC 驗證結果（靜態程式碼分析）

| AC | 條件 | 驗證方式 | 結果 |
|----|------|---------|------|
| AC-R8-01 | curl → HTTP 404 | UseStatusCodePagesWithReExecute 保留原 status code | ✅ PASS_code_analysis |
| AC-R8-02 | body.backgroundColor = rgb(241,247,248) | site.css `body { background-color: var(--color-bg-primary); }` → #F1F7F8 | ✅ PASS_code_analysis |
| AC-R8-03 | navbar.backgroundColor = rgb(17,208,115) | site.css `.navbar { background-color: var(--color-brand-primary) !important; }` → #11D073 | ✅ PASS_code_analysis |
| AC-R8-04 | snapshot 含「找不到頁面」 | Error.cshtml `@(code == 404 ? "找不到頁面！" : ...)` | ✅ PASS_code_analysis |
| AC-R8-05 | snapshot 含返回首頁 btn-primary | `<a href="/" class="btn btn-primary">返回首頁</a>` | ✅ PASS_code_analysis |

**SANDBOX LIMIT**：dotnet/git 指令封鎖。Playwright 即時驗證需 admin 將 worktree merge 後啟動 app 覆驗。

---

## 常見錯誤排除

| 問題 | 原因 | 解法 |
|------|------|------|
| /nonexistent-test 仍顯示 Chrome 預設 404 | `UseStatusCodePagesWithReExecute` 未生效 | 確認 Program.cs 中該行在 `MapControllerRoute` 之前 |
| Error 頁沒有 Navbar（純白無樣式）| Error.cshtml 沒用 `_Layout.cshtml` | 確認 `Layout = "~/Views/Shared/_Layout.cshtml";` 設定正確 |
| 按鈕不是翠綠（Bootstrap 預設藍）| `.btn-primary` 覆寫失效 | 確認 site.css 在 Bootstrap 之後載入（_Layout.cshtml 中的順序）|
| `/Error/404` 回 400 BadRequest | route constraint `{statusCode:int}` 未匹配 | 確認 URL 格式為 `/Error/404`（整數），`UseStatusCodePagesWithReExecute("/Error/{0}")` 正確 |

---

## 已知技術債

1. **HomeController.Error() 的 ViewData["StatusCode"] 未設定**：production 例外路徑（500）從 HomeController 進入時，
   Error.cshtml 收到 `code=0`，顯示「伺服器發生錯誤」（行為正確但不顯示狀態碼數字）。
   後續可在 HomeController.Error() 加入 `ViewData["StatusCode"] = 500;` 完善顯示。

2. **Attraction 類型 partial**：不在本卡 scope，但 ProductController 可能有 /Product/Detail 路由
   → 若 Attraction 頁 404，會正確顯示友善錯誤頁。

3. **SANDBOX LIMIT Playwright 覆驗**：AC-R8-01~05 僅靜態驗證，需 admin 在 merge 後啟動 app 完成 Playwright 覆驗。
