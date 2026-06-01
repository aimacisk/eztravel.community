using EzTravel.Community.Core.Enums;

namespace EzTravel.Community.Web.Models.ViewModels;

public class ProductDetailViewModel
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public ProductCategory Category { get; set; }
    public string? ImageUrl { get; set; }
    public int ReviewCount { get; set; }
    public double AverageRating { get; set; }
}
