using System.Text.Json;
using EzTravel.Community.Web.Models.ViewModels;

namespace EzTravel.Community.Web.Services;

public interface IPageDataLoader
{
    PageDataViewModel? Load(string slug);
    IReadOnlyList<CategoryInfo> ListCategories();
}

public class CategoryInfo
{
    public string Slug { get; init; } = string.Empty;
    public string DisplayName { get; init; } = string.Empty;
    public string FolderName { get; init; } = string.Empty;
}

public class PageDataLoader : IPageDataLoader
{
    private readonly IWebHostEnvironment _env;
    private readonly ILogger<PageDataLoader> _logger;
    private static readonly IReadOnlyList<CategoryInfo> Categories = new List<CategoryInfo>
    {
        new() { Slug = "homepage",  DisplayName = "首頁",     FolderName = "homepage" },
        new() { Slug = "flight",    DisplayName = "機票",     FolderName = "機票" },
        new() { Slug = "hotel",     DisplayName = "旅館",     FolderName = "旅館" },
        new() { Slug = "grouptour", DisplayName = "團體",     FolderName = "團體" },
        new() { Slug = "freetour",  DisplayName = "自由行",   FolderName = "自由行" },
        new() { Slug = "ticket",    DisplayName = "票券",     FolderName = "票券" },
        new() { Slug = "spot",      DisplayName = "景點",     FolderName = "景點" },
    };

    public PageDataLoader(IWebHostEnvironment env, ILogger<PageDataLoader> logger)
    {
        _env = env;
        _logger = logger;
    }

    public IReadOnlyList<CategoryInfo> ListCategories() => Categories;

    public PageDataViewModel? Load(string slug)
    {
        var info = Categories.FirstOrDefault(c => c.Slug.Equals(slug, StringComparison.OrdinalIgnoreCase));
        if (info is null) return null;

        // wwwroot/data/{FolderName}/{folderName}.json — runtime path inside container
        var dataRoot = Path.Combine(_env.WebRootPath, "data", info.FolderName);
        var jsonFileName = info.FolderName == "homepage" ? "homepage.json" : $"{info.FolderName}.json";
        var jsonPath = Path.Combine(dataRoot, jsonFileName);

        if (!File.Exists(jsonPath))
        {
            // 開發環境 fallback：從 project 根目錄的 data/ 讀
            var devDataRoot = Path.Combine(_env.ContentRootPath, "..", "..", "..", "..", "..", "data", info.FolderName);
            jsonPath = Path.Combine(devDataRoot, jsonFileName);
            if (!File.Exists(jsonPath))
            {
                _logger.LogWarning("找不到 page data: {Slug} (folder={Folder})", slug, info.FolderName);
                return null;
            }
        }

        var content = File.ReadAllText(jsonPath);
        var opts = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
        var model = JsonSerializer.Deserialize<PageDataViewModel>(content, opts);
        if (model is null) return null;

        model.CategorySlug = info.Slug;
        model.DisplayName = info.DisplayName;
        return model;
    }
}
