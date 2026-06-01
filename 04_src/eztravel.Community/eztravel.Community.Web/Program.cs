using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Interfaces.Services;
using EzTravel.Community.Infrastructure.Data;
using EzTravel.Community.Infrastructure.DependencyInjection;
using EzTravel.Community.Web.Services;
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

    // Middleware Pipeline
    if (!app.Environment.IsProduction())
        app.UseDeveloperExceptionPage();
    else
        app.UseExceptionHandler("/Home/Error");

    app.UseStaticFiles();
    app.UseRouting();
    app.UseAuthentication();
    app.UseAuthorization();
    app.UseSerilogRequestLogging();

    // /health endpoint for Cloud Run + Docker HEALTHCHECK
    app.MapGet("/health", () => Results.Ok(new { status = "ok", ts = DateTime.UtcNow }));

    // Route
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
