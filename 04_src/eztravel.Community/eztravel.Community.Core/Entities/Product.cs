using EzTravel.Community.Core.Enums;

namespace EzTravel.Community.Core.Entities;

public class Product
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public ProductCategory Category { get; set; }
    public string? ImageUrl { get; set; }
    public string? ExternalId { get; set; }
    public bool IsDeleted { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public ICollection<Review> Reviews { get; set; } = new List<Review>();
}
