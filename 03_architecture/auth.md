# Auth — ASP.NET Identity 配置規範

> **文件版本**：v1.0
> **建立日期**：2026-06-01 (TST)
> **負責人**：AT agent（T-eztcomm-20260601-W4-AT-1）
> **對應任務**：W4-AT-1 架構文件（三份之三）
> **上游規格**：community_spec.md §3 權限矩陣（W3-BA-1）
> **狀態**：APPROVED — W4-PG-1（Identity scaffold）與 W4-PG-4（Community feature）的單一依據

---

## §1 Identity 配置總覽

### 1.1 MVP 選型決策

| 面向 | 選擇 | 理由 |
|------|------|------|
| 認證方式 | Email + Password | MVP 簡單、無外部依賴 |
| Token 機制 | Cookie Authentication | MVC + Razor，Server-side render，Cookie 最自然 |
| Email confirm | **關閉**（MVP） | 降低開發複雜度；後續升級加入 |
| 外部 OAuth | 不實作（MVP 預留） | 降低複雜度；`appsettings` 保留 Google/Facebook 設定插槽 |
| Role-based 授權 | 是（`Member` / `Owner` / `Admin`） | 對齊 community_spec.md §3 RBAC |
| Policy-based 授權 | 是（細粒度操作授權） | 避免 Controller 大量 if/else（見 §4） |

### 1.2 角色定義對照（community_spec.md §3.1）

| Role 識別碼 | IdentityRole 名稱 | 對應 spec 角色 | 取得條件 |
|------------|-----------------|--------------|---------|
| （無 Role） | —（預設已登入使用者） | `Member` | 完成 email + password 註冊 |
| `Owner` | `"Owner"` | `Owner` | 管理員後台人工授予（MVP：`UserManager.AddToRoleAsync`） |
| `Admin` | `"Admin"` | `Admin` | 系統管理員；MVP 不實作後台 UI，由 seed 建立 |

> **MVP 假設**：`Owner` 角色由管理員以 `UserManager.AddToRoleAsync` 手動設定；後續實作後台 UI 時不需修改本文件。

---

## §2 DI 配置（`InfrastructureServiceExtensions`）

```csharp
// Identity 完整配置，於 AddInfrastructure() 呼叫
services.AddDefaultIdentity<ApplicationUser>(options =>
{
    // Password policy（平衡安全性與使用者友善）
    options.Password.RequireDigit           = true;
    options.Password.RequiredLength         = 8;
    options.Password.RequireUppercase       = false;  // MVP 放寬
    options.Password.RequireNonAlphanumeric = false;  // MVP 放寬
    options.Password.RequiredUniqueChars    = 1;

    // Email confirm 關閉（MVP）
    options.SignIn.RequireConfirmedEmail    = false;
    options.SignIn.RequireConfirmedAccount  = false;

    // Lockout（防暴力破解）
    options.Lockout.DefaultLockoutTimeSpan  = TimeSpan.FromMinutes(5);
    options.Lockout.MaxFailedAccessAttempts = 5;
    options.Lockout.AllowedForNewUsers      = true;

    // User settings
    options.User.AllowedUserNameCharacters =
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._@+";
    options.User.RequireUniqueEmail = true;
})
.AddRoles<IdentityRole>()
.AddEntityFrameworkStores<AppDbContext>()
.AddDefaultTokenProviders();  // 密碼重設 token 等用途

// Cookie 設定（見 §3）
services.ConfigureApplicationCookie(options =>
{
    options.Cookie.Name       = "EzTComm.Auth";
    options.Cookie.HttpOnly   = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
    options.Cookie.SameSite   = SameSiteMode.Lax;
    options.ExpireTimeSpan    = TimeSpan.FromDays(14);
    options.SlidingExpiration = true;
    options.LoginPath         = "/Account/Login";
    options.LogoutPath        = "/Account/Logout";
    options.AccessDeniedPath  = "/Account/AccessDenied";
});
```

---

## §3 Cookie 設定與安全規範

| Cookie 屬性 | 值 | 說明 |
|------------|-----|------|
| `Name` | `EzTComm.Auth` | 識別本站 cookie |
| `HttpOnly` | `true` | 防止 JavaScript 讀取（XSS 防護）|
| `Secure` | `Always` | 強制 HTTPS（生產環境必要）|
| `SameSite` | `Lax` | CSRF 基礎防護；允許跨站點 GET 導向（如 OAuth 回調）|
| `ExpireTimeSpan` | 14 天 | 維持登入狀態 2 週 |
| `SlidingExpiration` | `true` | 每次請求自動延展 14 天計時 |
| `LoginPath` | `/Account/Login` | 未登入時重導登入頁 |
| `AccessDeniedPath` | `/Account/AccessDenied` | 403 時導向說明頁 |

### 3.1 HTTPS 強制

```csharp
// Program.cs Middleware — 生產環境強制 HTTPS
if (app.Environment.IsProduction())
{
    app.UseHsts();
    app.UseHttpsRedirection();
}
```

> **Cloud Run 注意**：Cloud Run 負載平衡器終止 TLS，後端接收的是 HTTP。`app.UseHttpsRedirection()` 在 Cloud Run 應**設定信任代理 X-Forwarded-Proto**，避免無限重導。

```csharp
// Program.cs — Cloud Run 信任代理
builder.Services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    options.KnownNetworks.Clear();
    options.KnownProxies.Clear();
});
app.UseForwardedHeaders();
```

---

## §4 Policy-based 授權設計

### 4.1 Authorization Policy 定義

```csharp
// Program.cs 或 DI 設定
builder.Services.AddAuthorization(options =>
{
    // Community 操作 Policy
    options.AddPolicy("CanWriteReview",   p => p.RequireAuthenticatedUser());
    options.AddPolicy("CanDeleteOwnReview", p => p.RequireAuthenticatedUser());
    options.AddPolicy("CanLikeReview",    p => p.RequireAuthenticatedUser());
    options.AddPolicy("IsOwner",          p => p.RequireRole("Owner", "Admin"));
    options.AddPolicy("IsAdmin",          p => p.RequireRole("Admin"));
});
```

### 4.2 Controller 授權標記標準寫法

**原則**：Controller 只做授權標記（Attribute）；業務邏輯層次的權限判斷（如「只能改自己的評論」「24 小時時限」）在 **Service 層**實作。

```csharp
// ReviewController.cs
[ApiController]
[Route("api")]
public class ReviewController : ControllerBase
{
    private readonly IReviewService _reviewService;

    public ReviewController(IReviewService reviewService)
    {
        _reviewService = reviewService;
    }

    // 讀取評論 — 任何人可讀（含 Guest）
    [HttpGet("products/{productId:guid}/reviews")]
    [AllowAnonymous]
    public async Task<IActionResult> GetReviews(
        Guid productId,
        [FromQuery] ReviewListQuery query)
    { ... }

    // 新增評論 — 必須登入
    [HttpPost("products/{productId:guid}/reviews")]
    [Authorize(Policy = "CanWriteReview")]
    public async Task<IActionResult> CreateReview(
        Guid productId,
        [FromBody] CreateReviewRequest request)
    { ... }

    // 修改評論 — 必須登入（Service 層驗資格與時限）
    [HttpPatch("reviews/{reviewId:guid}")]
    [Authorize]
    public async Task<IActionResult> PatchReview(
        Guid reviewId,
        [FromBody] PatchReviewRequest request)
    { ... }

    // 刪除評論 — 必須登入（Service 層驗資格）
    [HttpDelete("reviews/{reviewId:guid}")]
    [Authorize]
    public async Task<IActionResult> DeleteReview(Guid reviewId)
    { ... }

    // 按讚 — 必須登入
    [HttpPost("reviews/{reviewId:guid}/like")]
    [Authorize(Policy = "CanLikeReview")]
    public async Task<IActionResult> LikeReview(Guid reviewId)
    { ... }

    // 取消讚 — 必須登入
    [HttpDelete("reviews/{reviewId:guid}/like")]
    [Authorize]
    public async Task<IActionResult> UnlikeReview(Guid reviewId)
    { ... }

    // 樓主回應 — 必須是 Owner 或 Admin
    [HttpPost("reviews/{parentReviewId:guid}/reply")]
    [Authorize(Policy = "IsOwner")]
    public async Task<IActionResult> AddOwnerReply(
        Guid parentReviewId,
        [FromBody] AddReplyRequest request)
    { ... }
}
```

### 4.3 取得目前登入使用者（標準寫法）

**Controller 層**：使用 `HttpContext.User`（注入 ClaimsPrincipal）

```csharp
// 取 UserId（string，對應 asp_net_users.id）
private string? GetCurrentUserId()
    => User.FindFirstValue(ClaimTypes.NameIdentifier);

// 在 [Authorize] Action 內使用
[HttpPost("reviews/{reviewId:guid}/like")]
[Authorize]
public async Task<IActionResult> LikeReview(Guid reviewId)
{
    var userId = GetCurrentUserId()!;  // [Authorize] 保證非 null
    var result = await _reviewService.LikeAsync(reviewId, userId);
    return result.IsSuccess ? StatusCode(201) : result.ToProblem();
}
```

**Service 層**（不直接依賴 HttpContext，接收 `userId` 字串）：

```csharp
// IReviewService
Task<ServiceResult> LikeAsync(Guid reviewId, string currentUserId, CancellationToken ct = default);
Task<ServiceResult> CreateAsync(Guid productId, CreateReviewDto dto, string currentUserId, CancellationToken ct = default);
Task<ServiceResult> PatchAsync(Guid reviewId, PatchReviewDto dto, string currentUserId, CancellationToken ct = default);
Task<ServiceResult> SoftDeleteAsync(Guid reviewId, string currentUserId, bool isAdmin, CancellationToken ct = default);
```

> **原則**：Service 不依賴 `IHttpContextAccessor`；Controller 負責取出 `userId` 傳入 Service，保持 Service 可測試性。

---

## §5 User Claim 設計

### 5.1 系統預設 Claims（由 ASP.NET Identity 自動填入）

| Claim Type | 值 | 說明 |
|-----------|-----|------|
| `ClaimTypes.NameIdentifier` | `ApplicationUser.Id` | 使用者主鍵（string）|
| `ClaimTypes.Email` | `user@example.com` | 電子郵件 |
| `ClaimTypes.Name` | `user@example.com` | UserName（預設 = Email）|
| `ClaimTypes.Role` | `"Owner"` / `"Admin"` | 角色（需授予 Role 後才有）|

### 5.2 Custom Claims（DisplayName + AvatarUrl）

`DisplayName` 與 `AvatarUrl` 為 `ApplicationUser` 的自訂屬性，**不加入 JWT/Cookie Claims**（避免 Cookie 膨脹），改以下方式在 Razor View 取用：

**View 層取用方式（UserManager 注入）**：

```csharp
// _ReviewCard.cshtml 或 _LoginPartial.cshtml
@inject UserManager<ApplicationUser> UserManager

@{
    var user = await UserManager.GetUserAsync(User);
    var displayName = user?.DisplayName ?? User.FindFirstValue(ClaimTypes.Email) ?? "匿名";
    var avatarUrl   = user?.AvatarUrl;
}
```

**API 回應中的使用者資訊**（由 Service 層查 DB 組裝）：

```json
{
  "user": {
    "id": "{{guid}}",
    "display_name": "旅遊達人 Wang",
    "avatar_url": "/uploads/avatar.jpg"
  }
}
```

> **設計理由**：`DisplayName` 可能被使用者更新，存 Cookie Claims 有快取一致性問題；每次請求從 DB 讀取雖有輕微成本，但 MVP 規模不成問題，且可搭配 `IMemoryCache` 暖快取。

---

## §6 登入 / 登出 / 註冊流程

### 6.1 使用 ASP.NET Identity 預設 Razor Pages

MVP 直接使用 `Microsoft.AspNetCore.Identity.UI` 提供的預設 Razor Pages，不重新實作：

| 路由 | 功能 |
|------|------|
| `/Account/Login` | 登入頁（email + password）|
| `/Account/Register` | 註冊頁 |
| `/Account/Logout` | 登出（POST）|
| `/Account/AccessDenied` | 403 說明頁 |
| `/Account/ForgotPassword` | 忘記密碼（MVP 可選）|

**啟用方式**（`Program.cs`）：

```csharp
// Identity Razor Pages 需要這兩行
builder.Services.AddRazorPages();
// ...
app.MapRazorPages();
```

### 6.2 Scaffold 客製化（選做 — 視 W4-PG 需求）

若需要修改預設頁面樣式（套用 eztravel 設計），執行以下 scaffold 產出可修改的 Razor Pages：

```bash
dotnet aspnet-codegenerator identity \
  --dbContext AppDbContext \
  --files "Account.Login;Account.Register;Account.Logout" \
  -p eztravel.Community.Web
```

產生位置：`Areas/Identity/Pages/Account/`

### 6.3 登入後 ReturnUrl 處理

未登入使用者觸發 `[Authorize]` → 自動重導至：

```
/Account/Login?ReturnUrl=%2Fproduct%2F11111111-0000-0000-0000-000000000001
```

Identity 登入成功後自動還原 `ReturnUrl`。Guest 操作行為（如按讚）對應 BA spec §6.6：

```javascript
// community.js — 未登入時前端導向登入頁
function requireLogin(returnUrl) {
    window.location.href = `/Account/Login?ReturnUrl=${encodeURIComponent(returnUrl)}`;
}
```

---

## §7 `_LoginPartial.cshtml` 介面元素

```cshtml
@using Microsoft.AspNetCore.Identity
@inject SignInManager<ApplicationUser> SignInManager
@inject UserManager<ApplicationUser> UserManager

@if (SignInManager.IsSignedIn(User))
{
    @* 已登入：顯示頭像 + 顯示名稱 + 登出 *@
    var currentUser = await UserManager.GetUserAsync(User);
    var displayName = currentUser?.DisplayName ?? User.Identity?.Name ?? "使用者";
    var avatarUrl   = currentUser?.AvatarUrl;

    <div class="nav-user-info d-flex align-items-center gap-2">
        @if (!string.IsNullOrEmpty(avatarUrl))
        {
            <img src="@avatarUrl" alt="頭像" class="avatar-sm rounded-circle" width="32" height="32" />
        }
        else
        {
            <div class="avatar-placeholder rounded-circle bg-primary text-white d-flex align-items-center justify-content-center"
                 style="width:32px;height:32px;font-size:14px;">
                @displayName[0]
            </div>
        }
        <span class="nav-display-name">@displayName</span>
        <form asp-area="Identity" asp-page="/Account/Logout" asp-route-returnUrl="@Url.Action("Index","Home")"
              method="post" class="d-inline">
            <button type="submit" class="btn btn-link nav-link p-0">登出</button>
        </form>
    </div>
}
else
{
    @* 未登入：顯示登入 + 註冊連結 *@
    <div class="nav-auth-links d-flex gap-3">
        <a asp-area="Identity" asp-page="/Account/Login"
           asp-route-returnUrl="@Context.Request.Path"
           class="btn btn-outline-primary btn-sm">登入</a>
        <a asp-area="Identity" asp-page="/Account/Register"
           class="btn btn-primary btn-sm">免費註冊</a>
    </div>
}
```

**引用方式**（`_Layout.cshtml`）：

```cshtml
<partial name="_LoginPartial" />
```

---

## §8 社群功能授權完整規則映射

對應 community_spec.md §3.2 操作權限矩陣，AT 此處定義每個操作對應的授權實作方式：

| 操作 | HTTP Method | 授權層次 | 實作方式 |
|------|------------|---------|---------|
| 讀取評論列表 | GET | `[AllowAnonymous]` | Controller Attribute |
| 讀取單筆評論 | GET | `[AllowAnonymous]` | Controller Attribute |
| 新增評論 | POST | `[Authorize]` | Controller Attribute；Service 驗 Rate limit |
| 編輯評論 | PATCH | `[Authorize]` | Controller Attribute；Service 驗擁有者 + 24h 時限 |
| 刪除評論（soft delete） | DELETE | `[Authorize]` | Controller Attribute；Service 驗擁有者 or Admin |
| 按讚評論 | POST | `[Authorize]` | Controller Attribute；Service 驗不能讚自己 + 不重複 |
| 取消讚 | DELETE | `[Authorize]` | Controller Attribute；Service 驗 like 存在 |
| 新增樓主回應 | POST | `[Authorize(Policy="IsOwner")]` | Controller Attribute；Service 驗商品擁有者 + 不重複 nested |

### 8.1 Service 層業務授權邏輯範本

```csharp
// ReviewService.PatchAsync — 授權 + 時限驗證
public async Task<ServiceResult> PatchAsync(
    Guid reviewId, PatchReviewDto dto, string currentUserId, CancellationToken ct = default)
{
    var review = await _reviewRepo.GetByIdAsync(reviewId, ct);
    if (review is null || review.IsDeleted) return ServiceResult.NotFound();

    // 1. 擁有者驗證（非 Admin 需是自己的評論）
    bool isAdmin = await _userManager.IsInRoleAsync(
        await _userManager.FindByIdAsync(currentUserId) ?? throw new(), "Admin");
    if (!isAdmin && review.UserId != currentUserId)
        return ServiceResult.Forbidden();

    // 2. 24 小時時限（非 Admin）
    if (!isAdmin && DateTimeOffset.UtcNow - review.CreatedAt > TimeSpan.FromHours(24))
        return ServiceResult.Forbidden("edit_window_expired");

    // 3. 更新欄位
    if (dto.Rating.HasValue) review.Rating = (short)dto.Rating.Value;
    if (dto.Text is not null) review.Text = SanitizeText(dto.Text);
    if (dto.Photos is not null) review.Photos = dto.Photos;
    review.UpdatedAt = DateTimeOffset.UtcNow;

    await _reviewRepo.UpdateAsync(review, ct);
    return ServiceResult.Ok(review);
}
```

---

## §9 角色種子（Development 環境）

```csharp
// Program.cs — 開發環境種子（啟動時執行）
if (app.Environment.IsDevelopment())
{
    using var scope = app.Services.CreateScope();
    var roleManager = scope.ServiceProvider.GetRequiredService<RoleManager<IdentityRole>>();
    var userManager = scope.ServiceProvider.GetRequiredService<UserManager<ApplicationUser>>();

    // 建立角色
    foreach (var role in new[] { "Owner", "Admin" })
    {
        if (!await roleManager.RoleExistsAsync(role))
            await roleManager.CreateAsync(new IdentityRole(role));
    }

    // 建立預設 Admin 帳號
    const string adminEmail = "admin@eztravel.test";
    if (await userManager.FindByEmailAsync(adminEmail) is null)
    {
        var admin = new ApplicationUser
        {
            UserName    = adminEmail,
            Email       = adminEmail,
            DisplayName = "EzTravel Admin",
            EmailConfirmed = true
        };
        await userManager.CreateAsync(admin, "Admin@12345");
        await userManager.AddToRoleAsync(admin, "Admin");
    }
}
```

---

## §10 安全性注意事項

| 事項 | 規範 |
|------|------|
| **密碼重設** | MVP 使用預設 Identity token（短效期）；注意 Cloud Run 多節點時 `DataProtection` key 需持久化（可用 GCP KMS）|
| **CSRF 防護** | Identity 預設 Razor Pages 包含 `[ValidateAntiForgeryToken]`；AJAX API endpoint 改用 cookie-based 驗證已足夠（SameSite=Lax）|
| **Rate Limit（登入）** | Identity Lockout（5 次失敗鎖 5 分鐘）已在 §2 設定 |
| **XSS** | Razor 預設 HTML encode（`@Model.Text`）；禁用 `@Html.Raw`；文字存入前 Service 層 `SanitizeText()`（見 community_spec.md §5.4）|
| **SQL Injection** | EF Core parameterized query，所有查詢走 LINQ；禁止拼接 raw SQL |
| **Cookie 安全** | `HttpOnly=true` + `Secure=Always`；Cloud Run 前的 HTTPS 終止需信任 X-Forwarded-Proto（見 §3.1）|

---

## §11 驗收條件（對應卡片 verification）

| 條件 | 驗證方式 |
|------|---------|
| 本文件行數 ≥ 150 | `wc -l auth.md` |
| 含 Identity DI 配置（含 email confirm 關閉說明） | grep 驗證 |
| 含 Cookie 設定完整表格 | 人工驗核 §3 |
| 含 Policy 定義（IsOwner / IsAdmin） | grep 驗證 |
| 含 `_LoginPartial.cshtml` 實作 | 人工驗核 §7 |
| 含取得 current user 標準寫法 | 人工驗核 §4.3 |

---

*文件結束。社群 RBAC 變更需同步更新 community_spec.md §3，AT 接受 REWORK 卡。*
