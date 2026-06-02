# Solution Layout — eztravel.Community .NET 8 MVC

> **文件版本**：v1.0
> **建立日期**：2026-06-01 (TST)
> **負責人**：AT agent（T-eztcomm-20260601-W4-AT-1）
> **對應任務**：W4-AT-1 架構文件（三份之一）
> **狀態**：APPROVED — W4-AT-2（基底骨架實作）與 W4-PG-*（業務實作）的單一規格依據

---

## §1 Solution 根目錄結構

```
projects/eztravel.community/
├── 01_requirements/
├── 02_design/
├── 03_architecture/                    ← AT 產出（本文件所在）
├── 04_src/
│   └── eztravel.Community/             ← .NET Solution 根目錄
│       ├── eztravel.Community.sln
│       ├── eztravel.Community.Web/
│       ├── eztravel.Community.Core/
│       ├── eztravel.Community.Infrastructure/
│       └── eztravel.Community.Tests/
├── data/
│   ├── homepage/
│   ├── 機票/
│   ├── 旅館/
│   ├── 團體/
│   ├── 自由行/
│   ├── 票券/
│   └── 景點/
├── .github/
│   └── workflows/
│       └── release.yml
├── Dockerfile
└── README.md
```

---

## §2 四個 csproj 設計

### 2.1 依賴方向圖（DAG — 不允許循環）

```
eztravel.Community.Web
  │
  ├── → eztravel.Community.Core        (Domain entities + Interfaces)
  └── → eztravel.Community.Infrastructure
                │
                └── → eztravel.Community.Core

eztravel.Community.Tests
  │
  ├── → eztravel.Community.Web         (WebApplicationFactory)
  ├── → eztravel.Community.Core
  └── → eztravel.Community.Infrastructure
```

**原則**：Core 不依賴任何其他層；Infrastructure 只依賴 Core；Web 依賴 Core + Infrastructure。

---

### 2.2 `eztravel.Community.Core` — Domain Layer

**職責**：純 POCO Domain 物件、介面定義、列舉、Value Objects。**無任何框架依賴**。

**Target Framework**：`net8.0`（Class Library）

**目錄結構**：

```
eztravel.Community.Core/
├── eztravel.Community.Core.csproj
├── Entities/
│   ├── ApplicationUser.cs              # IdentityUser 擴充（DisplayName, AvatarUrl）
│   ├── Product.cs
│   ├── Review.cs
│   └── ReviewLike.cs
├── Enums/
│   └── ProductCategory.cs              # GroupTour / FreeTour / Hotel / Ticket
├── Interfaces/
│   ├── Repositories/
│   │   ├── IProductRepository.cs
│   │   ├── IReviewRepository.cs
│   │   └── IReviewLikeRepository.cs
│   └── Services/
│       ├── IReviewService.cs
│       └── IProductService.cs
└── Models/
    ├── ReviewSummary.cs                # 聚合摘要 DTO（average_rating / total_reviews 等）
    ├── ReviewListQuery.cs              # FilterBar 查詢參數（stars / hasPhoto / sort / page）
    └── ReviewListResult.cs             # 分頁回應（total_count / has_next_page / items）
```

**csproj 內容**：

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
```

---

### 2.3 `eztravel.Community.Infrastructure` — Data Layer

**職責**：EF Core DbContext、Repository 實作、ASP.NET Identity 配置、Migration、Seed 資料。

**Target Framework**：`net8.0`（Class Library）

**套件依賴**：

| 套件 | 版本 | 用途 |
|------|------|------|
| `Microsoft.EntityFrameworkCore` | 8.x | ORM 核心 |
| `Npgsql.EntityFrameworkCore.PostgreSQL` | 8.x | PostgreSQL provider |
| `Microsoft.AspNetCore.Identity.EntityFrameworkCore` | 8.x | Identity + EF Core 整合 |
| `Microsoft.Extensions.Caching.Memory` | 8.x | IMemoryCache（聚合快取） |

**目錄結構**：

```
eztravel.Community.Infrastructure/
├── eztravel.Community.Infrastructure.csproj
├── Data/
│   ├── AppDbContext.cs                 # IdentityDbContext<ApplicationUser> 繼承
│   ├── Configurations/
│   │   ├── ProductConfiguration.cs     # IEntityTypeConfiguration<Product>
│   │   ├── ReviewConfiguration.cs
│   │   └── ReviewLikeConfiguration.cs
│   └── Migrations/
│       ├── Initial/                    # 初始 DB + Identity tables
│       ├── AddCommunity/               # Review / ReviewLike tables
│       └── SeedProducts/               # 從 data/ JSON 載入種子商品
├── Repositories/
│   ├── ProductRepository.cs
│   ├── ReviewRepository.cs
│   └── ReviewLikeRepository.cs
└── DependencyInjection/
    └── InfrastructureServiceExtensions.cs  # AddInfrastructure() 擴充方法
```

**csproj 內容**：

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\eztravel.Community.Core\eztravel.Community.Core.csproj" />
  </ItemGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.*" />
    <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.*" />
    <PackageReference Include="Microsoft.AspNetCore.Identity.EntityFrameworkCore" Version="8.*" />
    <PackageReference Include="Microsoft.Extensions.Caching.Memory" Version="8.*" />
  </ItemGroup>
</Project>
```

---

### 2.4 `eztravel.Community.Web` — Presentation Layer

**職責**：ASP.NET Core MVC 主啟動專案、Controllers、Views（Razor）、Partial Views、靜態資源、DI 組裝。

**Target Framework**：`net8.0`（Web SDK）

**套件依賴**：

| 套件 | 版本 | 用途 |
|------|------|------|
| `Serilog.AspNetCore` | 8.x | Structured logging |
| `Serilog.Formatting.Compact` | 2.x | stdout JSON 格式（Cloud Logging）|
| `Serilog.Enrichers.Environment` | 2.x | MachineName 等環境欄位 |
| `Serilog.Enrichers.Span` | 3.x | TraceId / SpanId 帶入 log |
| `Microsoft.AspNetCore.Identity.UI` | 8.x | Identity Razor Pages 預設 UI |

**目錄結構**：

```
eztravel.Community.Web/
├── eztravel.Community.Web.csproj
├── Program.cs                          # 應用程式入口 + Serilog 配置
├── appsettings.json                    # 通用設定（Serilog Minimum Level）
├── appsettings.Development.json        # Dev：Console 文字格式 + localhost DB
├── appsettings.Production.json         # Prod：stdout JSON + Cloud SQL Unix socket
├── Controllers/
│   ├── HomeController.cs               # / 首頁
│   ├── CategoryController.cs           # /機票、/旅館、/團體、/自由行、/票券、/景點
│   ├── ProductController.cs            # /product/{id} 商品詳情
│   ├── ReviewController.cs             # /api/... Community AJAX endpoints
│   └── HealthController.cs             # /health
├── Models/
│   └── ViewModels/
│       ├── HomeViewModel.cs
│       ├── CategoryViewModel.cs
│       ├── ProductDetailViewModel.cs
│       └── ReviewViewModel.cs
├── Views/
│   ├── Home/
│   │   └── Index.cshtml
│   ├── Category/
│   │   └── Index.cshtml                # 6 個分類頁共用樣板
│   ├── Product/
│   │   └── Detail.cshtml
│   ├── Shared/
│   │   ├── _Layout.cshtml
│   │   ├── _LoginPartial.cshtml        # 詳見 auth.md §3
│   │   ├── _ReviewList.cshtml          # 評論列表 partial
│   │   ├── _ReviewCard.cshtml          # 單筆評論卡片 partial
│   │   ├── _ReviewComposer.cshtml      # 撰寫評論 partial
│   │   ├── _RatingDistribution.cshtml  # 星等分布圖 partial
│   │   └── _FilterBar.cshtml           # 篩選列 partial
│   └── _ViewImports.cshtml
├── Services/
│   └── ReviewService.cs                # 業務邏輯（依賴注入自 Infrastructure）
├── wwwroot/
│   ├── css/
│   │   ├── site.css
│   │   └── community.css               # Community 模組樣式
│   ├── js/
│   │   ├── site.js
│   │   └── community.js                # 按讚 / Optimistic Update / FilterBar SPA 邏輯
│   └── uploads/                        # 使用者上傳圖片（MVP wwwroot，Cloud Run 無狀態限制）
└── Properties/
    └── launchSettings.json
```

**csproj 內容**：

```xml
<Project Sdk="Microsoft.NET.Web.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\eztravel.Community.Core\eztravel.Community.Core.csproj" />
    <ProjectReference Include="..\eztravel.Community.Infrastructure\eztravel.Community.Infrastructure.csproj" />
  </ItemGroup>
  <ItemGroup>
    <PackageReference Include="Serilog.AspNetCore" Version="8.*" />
    <PackageReference Include="Serilog.Formatting.Compact" Version="2.*" />
    <PackageReference Include="Serilog.Enrichers.Environment" Version="2.*" />
    <PackageReference Include="Serilog.Enrichers.Span" Version="3.*" />
    <PackageReference Include="Microsoft.AspNetCore.Identity.UI" Version="8.*" />
  </ItemGroup>
</Project>
```

---

### 2.5 `eztravel.Community.Tests` — Test Layer

**職責**：xUnit 單元測試（Core + Service）、整合測試（WebApplicationFactory + Testcontainers）。

**Target Framework**：`net8.0`（Class Library）

**套件依賴**：

| 套件 | 版本 | 用途 |
|------|------|------|
| `xunit` | 2.x | 測試框架 |
| `xunit.runner.visualstudio` | 2.x | VS / CI runner |
| `Moq` | 4.x | Mock 框架 |
| `Microsoft.AspNetCore.Mvc.Testing` | 8.x | WebApplicationFactory |
| `Testcontainers.PostgreSql` | 3.x | 整合測試用真實 PostgreSQL container |
| `FluentAssertions` | 6.x | 可讀斷言 |

**目錄結構**：

```
eztravel.Community.Tests/
├── eztravel.Community.Tests.csproj
├── Unit/
│   ├── ReviewServiceTests.cs           # 評論建立 / 更新 / 刪除業務規則
│   ├── ReviewLikeServiceTests.cs       # 按讚 / 取消讚規則
│   └── RatingSummaryTests.cs           # 聚合計算正確性
└── Integration/
    ├── WebFactory.cs                    # CustomWebApplicationFactory<Program>
    ├── ReviewApiTests.cs               # GET/POST/PATCH/DELETE /api/reviews 整合測試
    └── AuthTests.cs                    # 登入 / 登出 / 未授權 401 測試
```

---

## §3 DI 組裝規範

**原則**：所有依賴注入集中在 `Program.cs` 與各層的 `ServiceExtensions`；Controller 不直接 `new` 任何服務。

### 3.1 `Program.cs` 結構

```csharp
// 1. Serilog 最優先配置（Bootstrap logger 處理啟動錯誤）
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .CreateBootstrapLogger();

var builder = WebApplication.CreateBuilder(args);

// 2. Serilog Host 配置
builder.Host.UseSerilog((ctx, lc) => lc
    .ReadFrom.Configuration(ctx.Configuration)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithSpan()
    .WriteTo.Console(
        env.IsProduction()
            ? new RenderedCompactJsonFormatter()  // stdout JSON → Cloud Logging
            : new ConsoleThemeTextFormatter()     // Dev 可讀格式
    ));

// 3. Infrastructure 層（EF Core + Identity + IMemoryCache）
builder.Services.AddInfrastructure(builder.Configuration);

// 4. Application 服務
builder.Services.AddScoped<IReviewService, ReviewService>();
builder.Services.AddScoped<IProductService, ProductService>();

// 5. MVC + Razor
builder.Services.AddControllersWithViews();
builder.Services.AddRazorPages(); // Identity Razor Pages 需要

// 6. 建置 app
var app = builder.Build();

// 7. 啟動時套用 EF Migration（開發/生產共用）
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.Migrate();
}

// 8. Middleware Pipeline
if (!app.Environment.IsProduction())
    app.UseDeveloperExceptionPage();
else
    app.UseExceptionHandler("/Home/Error");

app.UseStaticFiles();
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.UseSerilogRequestLogging();

// 9. Route 設定
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
app.MapRazorPages(); // Identity /Account/* pages

app.Run();
```

### 3.2 `InfrastructureServiceExtensions.AddInfrastructure()`

```csharp
public static IServiceCollection AddInfrastructure(
    this IServiceCollection services,
    IConfiguration configuration)
{
    // EF Core + PostgreSQL
    services.AddDbContext<AppDbContext>(opts =>
        opts.UseNpgsql(configuration.GetConnectionString("DefaultConnection")));

    // ASP.NET Identity
    services.AddDefaultIdentity<ApplicationUser>(opts =>
    {
        opts.Password.RequireDigit = true;
        opts.Password.RequiredLength = 8;
        opts.SignIn.RequireConfirmedEmail = false;  // MVP 關閉
    })
    .AddRoles<IdentityRole>()
    .AddEntityFrameworkStores<AppDbContext>();

    // Repository 注入
    services.AddScoped<IProductRepository, ProductRepository>();
    services.AddScoped<IReviewRepository, ReviewRepository>();
    services.AddScoped<IReviewLikeRepository, ReviewLikeRepository>();

    // 快取（聚合摘要用）
    services.AddMemoryCache();

    return services;
}
```

---

## §4 命名規範

### 4.1 命名空間

| 層級 | 命名空間模式 | 範例 |
|------|------------|------|
| Core Entities | `EzTravel.Community.Core.Entities` | `ApplicationUser`, `Product` |
| Core Interfaces | `EzTravel.Community.Core.Interfaces.Repositories` | `IReviewRepository` |
| Core Models（DTO） | `EzTravel.Community.Core.Models` | `ReviewSummary` |
| Core Enums | `EzTravel.Community.Core.Enums` | `ProductCategory` |
| Infrastructure Data | `EzTravel.Community.Infrastructure.Data` | `AppDbContext` |
| Infrastructure Repos | `EzTravel.Community.Infrastructure.Repositories` | `ReviewRepository` |
| Web Controllers | `EzTravel.Community.Web.Controllers` | `ReviewController` |
| Web ViewModels | `EzTravel.Community.Web.Models.ViewModels` | `ProductDetailViewModel` |
| Web Services | `EzTravel.Community.Web.Services` | `ReviewService` |

### 4.2 檔案與類別命名

| 類型 | 規則 | 正確範例 | 錯誤範例 |
|------|------|---------|---------|
| Entity | `{EntityName}.cs` | `Review.cs` | `ReviewEntity.cs` |
| Repository 介面 | `I{Entity}Repository.cs` | `IReviewRepository.cs` | `IReviewRepo.cs` |
| Repository 實作 | `{Entity}Repository.cs` | `ReviewRepository.cs` | `ReviewRepo.cs` |
| Service 介面 | `I{Domain}Service.cs` | `IReviewService.cs` | `IReviewSvc.cs` |
| Controller | `{Domain}Controller.cs` | `ReviewController.cs` | `ReviewsController.cs` |
| ViewModel | `{Page}ViewModel.cs` | `ProductDetailViewModel.cs` | `ProductDetailVM.cs` |
| Razor Partial | `_{ComponentName}.cshtml` | `_ReviewCard.cshtml` | `ReviewCard.cshtml` |

### 4.3 DB Column 命名（EF Core Convention）

EF Core 預設 PascalCase → snake_case（Npgsql 設定 `UseSnakeCaseNamingConvention()`）。

| C# Property | DB Column |
|-------------|----------|
| `Id` | `id` |
| `ProductId` | `product_id` |
| `UserId` | `user_id` |
| `HelpfulCount` | `helpful_count` |
| `IsDeleted` | `is_deleted` |
| `CreatedAt` | `created_at` |
| `ParentReviewId` | `parent_review_id` |

---

## §5 靜態資源策略

### 5.1 wwwroot 圖片同步

Build 時（或啟動前）將 `data/{category}/images/` 目錄下所有圖片複製到 `wwwroot/images/{category}/`。

```
wwwroot/
├── images/
│   ├── homepage/    ← 從 data/homepage/images/ 複製
│   ├── flight/      ← 從 data/機票/images/ 複製
│   ├── hotel/       ← 從 data/旅館/images/ 複製
│   ├── group/       ← 從 data/團體/images/ 複製
│   ├── freetour/    ← 從 data/自由行/images/ 複製
│   ├── ticket/      ← 從 data/票券/images/ 複製
│   └── attraction/  ← 從 data/景點/images/ 複製
└── uploads/         ← 使用者上傳（MVP wwwroot，後續升級至 GCS）
```

**實作方式**：`Dockerfile` 在 build stage 以 `COPY data/ /app/data/` + 啟動腳本複製至 wwwroot。

### 5.2 Bundle 策略（MVP）

MVP 不使用 Webpack / Vite，直接以 `<link>` / `<script>` 引用靜態 CSS/JS。未來擴充需求由 W5 升級時評估。

---

## §6 連線字串設計

### 6.1 開發環境（Dev — Docker PostgreSQL）

```json
// appsettings.Development.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=eztcomm_dev;Username=postgres;Password=devpassword"
  }
}
```

### 6.2 生產環境（Prod — GCP Cloud SQL Unix socket）

```json
// appsettings.Production.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=/cloudsql/{INSTANCE_CONNECTION_NAME};Database=eztcomm_prod;Username=eztcomm_app;Password={SECRET}"
  }
}
```

**注意**：`{INSTANCE_CONNECTION_NAME}` 格式為 `{project}:{region}:{instance}`，例如 `eztcomm-prod-1780402352:asia-east1:eztcomm-db`。實際值由 GCP Secret Manager 注入至環境變數，不硬寫在 appsettings。

---

## §7 Serilog 設定規範

```json
// appsettings.json（通用）
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft.AspNetCore": "Warning",
        "Microsoft.EntityFrameworkCore.Database.Command": "Warning"
      }
    }
  }
}
```

**Severity 對應**：

| Serilog Level | Cloud Logging Severity |
|--------------|----------------------|
| Verbose / Debug | DEBUG |
| Information | INFO |
| Warning | WARNING |
| Error | ERROR |
| Fatal | CRITICAL |

---

## §8 launchSettings.json（本機開發）

```json
{
  "profiles": {
    "http": {
      "commandName": "Project",
      "dotnetRunMessages": true,
      "launchBrowser": true,
      "applicationUrl": "http://localhost:5150",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development"
      }
    },
    "Docker": {
      "commandName": "Docker",
      "launchBrowser": true,
      "launchUrl": "{Scheme}://{ServiceHost}:{ServicePort}",
      "publishAllPorts": true
    }
  }
}
```

---

## §9 Solution 建立指令參考（供 W4-AT-2 執行）

```bash
# 在 04_src/ 目錄下執行
dotnet new sln -n eztravel.Community

dotnet new classlib -n eztravel.Community.Core       -f net8.0
dotnet new classlib -n eztravel.Community.Infrastructure -f net8.0
dotnet new mvc      -n eztravel.Community.Web        -f net8.0
dotnet new xunit    -n eztravel.Community.Tests      -f net8.0

dotnet sln add eztravel.Community.Core/eztravel.Community.Core.csproj
dotnet sln add eztravel.Community.Infrastructure/eztravel.Community.Infrastructure.csproj
dotnet sln add eztravel.Community.Web/eztravel.Community.Web.csproj
dotnet sln add eztravel.Community.Tests/eztravel.Community.Tests.csproj

# 設定 ProjectReference（DAG 方向）
dotnet add eztravel.Community.Infrastructure reference eztravel.Community.Core
dotnet add eztravel.Community.Web reference eztravel.Community.Core
dotnet add eztravel.Community.Web reference eztravel.Community.Infrastructure
dotnet add eztravel.Community.Tests reference eztravel.Community.Web
dotnet add eztravel.Community.Tests reference eztravel.Community.Core
dotnet add eztravel.Community.Tests reference eztravel.Community.Infrastructure
```

---

## §10 驗收條件（對應卡片 verification）

| 條件 | 驗證方式 |
|------|---------|
| 本文件存在且行數 ≥ 150 | `wc -l solution_layout.md` |
| solution 結構含 4 個 csproj 名稱 | grep 驗證 |
| 依賴方向圖存在且無循環依賴描述 | 人工驗核 §2.1 |
| DI 組裝規範含 AddInfrastructure() | grep 驗證 |
| 命名規範含 snake_case DB column 對應表 | 人工驗核 §4.3 |

---

*文件結束。如有疑義請依 community_spec.md §9.2 或向 AT 提出 REWORK。*
