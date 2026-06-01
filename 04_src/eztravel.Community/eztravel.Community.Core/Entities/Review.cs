namespace EzTravel.Community.Core.Entities;

public class Review
{
    public int Id { get; set; }
    public int ProductId { get; set; }
    public string UserId { get; set; } = string.Empty;
    public int Rating { get; set; }
    public string? Title { get; set; }
    public string? Body { get; set; }
    public string? PhotoUrl { get; set; }
    public int? ParentReviewId { get; set; }
    public int HelpfulCount { get; set; }
    public bool IsDeleted { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? UpdatedAt { get; set; }

    public Product? Product { get; set; }
    public ApplicationUser? User { get; set; }
    public Review? ParentReview { get; set; }
    public ICollection<ReviewLike> Likes { get; set; } = new List<ReviewLike>();
}
