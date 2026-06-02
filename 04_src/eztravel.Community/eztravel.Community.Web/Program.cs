using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Enums;
using EzTravel.Community.Core.Interfaces.Services;
using EzTravel.Community.Infrastructure.Data;
using EzTravel.Community.Infrastructure.DependencyInjection;
using EzTravel.Community.Web.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Serilog;
using Serilog.Formatting.Compact;

// Bootstrap logger — 捕捉啟動期間的錯誤
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .CreateBootstrapLogger();

try
{
    var builder = WebApplication.CreateBuilder(args);

    // Serilog Host 配置
    builder.Host.UseSerilog((ctx, lc) =>
    {
        lc.ReadFrom.Configuration(ctx.Configuration)
          .Enrich.FromLogContext()
          .Enrich.WithMachineName()
          .Enrich.WithProperty("AppVersion", typeof(Program).Assembly.GetName().Version?.ToString() ?? "unknown");

        if (ctx.HostingEnvironment.IsProduction())
            lc.WriteTo.Console(new RenderedCompactJsonFormatter());
        else
            lc.WriteTo.Console();
    });

    // Infrastructure 層（EF Core + Repository + IMemoryCache）
    builder.Services.AddInfrastructure(builder.Configuration);

    // ASP.NET Identity（AddDefaultIdentity 需要 Identity.UI；Roles 支援另加 AddRoles）
    builder.Services.AddDefaultIdentity<ApplicationUser>(opts =>
    {
        opts.Password.RequireDigit = true;
        opts.Password.RequiredLength = 8;
        opts.SignIn.RequireConfirmedEmail = false;
    })
    .AddRoles<IdentityRole>()
    .AddEntityFrameworkStores<AppDbContext>();

    // BUG-006 修復：/api/* 未授權時回 401，而非 302 重定向 Login（[ApiController] REST 慣例）
    builder.Services.ConfigureApplicationCookie(opts =>
    {
        opts.Events.OnRedirectToLogin = ctx =>
        {
            if (ctx.Request.Path.StartsWithSegments("/api"))
                ctx.Response.StatusCode = StatusCodes.Status401Unauthorized;
            else
                ctx.Response.Redirect(ctx.RedirectUri);
            return Task.CompletedTask;
        };
        opts.Events.OnRedirectToAccessDenied = ctx =>
        {
            if (ctx.Request.Path.StartsWithSegments("/api"))
                ctx.Response.StatusCode = StatusCodes.Status403Forbidden;
            else
                ctx.Response.Redirect(ctx.RedirectUri);
            return Task.CompletedTask;
        };
    });

    // Application 服務（骨架空殼，業務邏輯由 W4-PG-* 填入）
    builder.Services.AddScoped<IReviewService, ReviewService>();
    builder.Services.AddScoped<IProductService, ProductService>();

    // Page data loader (從 wwwroot/data 載入 W1 爬蟲資料)
    builder.Services.AddSingleton<EzTravel.Community.Web.Services.IPageDataLoader, EzTravel.Community.Web.Services.PageDataLoader>();

    // MVC + Razor Pages（Identity UI 需要）
    builder.Services.AddControllersWithViews();
    builder.Services.AddRazorPages();

    var app = builder.Build();

    // Production: 啟動前自動套用 migration
    if (app.Environment.IsProduction())
    {
        using var scope = app.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        await db.Database.MigrateAsync();
        Log.Information("Production migration 套用完成");
    }

    // Development: InMemory DB 建立 schema + 注入測試用種子資料
    if (app.Environment.IsDevelopment())
    {
        using var scope = app.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        await db.Database.EnsureCreatedAsync();
        if (!db.Products.Any())
        {
            db.Products.AddRange(
                new Product { Id = 1, Name = "日本東京自由行 5 天 4 夜", Category = ProductCategory.FreeTour, Description = "含來回機票、飯店住宿，自由探索東京精華景點", CreatedAt = DateTime.UtcNow },
                new Product { Id = 2, Name = "泰國曼谷團體深度旅遊", Category = ProductCategory.GroupTour, Description = "含機票、飯店、全程專業導遊陪同", CreatedAt = DateTime.UtcNow },
                new Product { Id = 3, Name = "沖繩海濱飯店 3 晚自由行", Category = ProductCategory.Hotel, Description = "太平洋視野套房，含早餐，近美麗海水族館", CreatedAt = DateTime.UtcNow },
                new Product { Id = 4, Name = "環球影城一日票", Category = ProductCategory.Ticket, Description = "成人票，一日暢遊主題樂園", CreatedAt = DateTime.UtcNow }
            );
            await db.SaveChangesAsync();
            Log.Information("Development 種子資料注入完成（4 筆 Product）");
        }
    }

    // Middleware Pipeline
    if (!app.Environment.IsProduction())
        app.UseDeveloperExceptionPage();
    else
        app.UseExceptionHandler("/Home/Error");

    // 404/500 等 HTTP status code 走 Error 頁(套主 layout 含 site.css 翠綠)
    app.UseStatusCodePagesWithReExecute("/Home/Error/{0}");

    app.UseStaticFiles();
    app.UseRouting();
    app.UseAuthentication();
    app.UseAuthorization();
    app.UseSerilogRequestLogging();

    // Route  (注意: /health 由 HealthController 提供，避免 AmbiguousMatchException)
    app.MapControllerRoute(
        name: "default",
        pattern: "{controller=Home}/{action=Index}/{id?}");
    app.MapRazorPages();

    Log.Information("eztravel.Community 啟動中，環境={Environment}", app.Environment.EnvironmentName);
    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "應用程式啟動失敗");
    throw;
}
finally
{
    Log.CloseAndFlush();
}
