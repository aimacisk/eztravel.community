namespace EzTravel.Community.Core.Entities;

public class ReviewLike
{
    public int Id { get; set; }
    public int ReviewId { get; set; }
    public string UserId { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public Review? Review { get; set; }
    public ApplicationUser? User { get; set; }
}
