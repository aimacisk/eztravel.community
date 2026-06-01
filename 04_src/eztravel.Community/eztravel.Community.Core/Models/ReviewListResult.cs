using EzTravel.Community.Core.Entities;

namespace EzTravel.Community.Core.Models;

public class ReviewListResult
{
    public int TotalCount { get; set; }
    public bool HasNextPage { get; set; }
    public IReadOnlyList<Review> Items { get; set; } = Array.Empty<Review>();
}
