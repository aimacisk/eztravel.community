namespace EzTravel.Community.Core.Models;

public class ReviewListQuery
{
    public int ProductId { get; set; }
    public int? Stars { get; set; }
    public bool? HasPhoto { get; set; }
    public string Sort { get; set; } = "newest";
    public int Page { get; set; } = 1;
    public int PageSize { get; set; } = 10;
}
