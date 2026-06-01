using EzTravel.Community.Core.Interfaces.Repositories;
using EzTravel.Community.Infrastructure.Data;
using EzTravel.Community.Infrastructure.Repositories;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace EzTravel.Community.Infrastructure.DependencyInjection;

public static class InfrastructureServiceExtensions
{
    /// <summary>
    /// 注冊 EF Core DbContext、Repository 與 IMemoryCache。
    /// Identity 設定（AddDefaultIdentity + Roles）由呼叫方（Program.cs）負責，
    /// 以確保 Identity UI Razor Pages 套件僅在 Web 層引用。
    /// </summary>
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        var connStr = configuration.GetConnectionString("DefaultConnection");
        if (!string.IsNullOrWhiteSpace(connStr))
        {
            services.AddDbContext<AppDbContext>(opts =>
                opts.UseNpgsql(connStr).UseSnakeCaseNamingConvention());
        }
        else
        {
            // 骨架階段：無 DB 連線字串時使用 InMemory（讓 dotnet run 可啟動）
            services.AddDbContext<AppDbContext>(opts =>
                opts.UseInMemoryDatabase("eztcomm_dev"));
        }

        services.AddScoped<IProductRepository, ProductRepository>();
        services.AddScoped<IReviewRepository, ReviewRepository>();
        services.AddScoped<IReviewLikeRepository, ReviewLikeRepository>();
        services.AddMemoryCache();

        return services;
    }
}
