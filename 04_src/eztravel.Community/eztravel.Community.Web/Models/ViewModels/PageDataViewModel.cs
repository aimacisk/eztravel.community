using System.Text.Json.Serialization;

namespace EzTravel.Community.Web.Models.ViewModels;

public class PageDataViewModel
{
    [JsonPropertyName("page")]
    public string Page { get; set; } = string.Empty;

    [JsonPropertyName("scraped_at")]
    public string? ScrapedAt { get; set; }

    [JsonPropertyName("url")]
    public string? Url { get; set; }

    [JsonPropertyName("sections")]
    public List<SectionViewModel> Sections { get; set; } = new();

    public string CategorySlug { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
}

public class SectionViewModel
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;

    [JsonPropertyName("title")]
    public string? Title { get; set; }

    [JsonPropertyName("items")]
    public List<SectionItemViewModel> Items { get; set; } = new();
}

public class SectionItemViewModel
{
    [JsonPropertyName("text")]
    public string? Text { get; set; }

    [JsonPropertyName("image_url")]
    public string? ImageUrl { get; set; }

    [JsonPropertyName("link_url")]
    public string? LinkUrl { get; set; }

    [JsonPropertyName("price")]
    public string? Price { get; set; }

    [JsonPropertyName("badge")]
    public string? Badge { get; set; }

    [JsonPropertyName("description")]
    public string? Description { get; set; }
}
