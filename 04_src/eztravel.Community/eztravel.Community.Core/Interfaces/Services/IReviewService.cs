using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Models;

namespace EzTravel.Community.Core.Interfaces.Services;

public interface IReviewService
{
    Task<ReviewListResult> GetReviewsAsync(ReviewListQuery query, CancellationToken ct = default);
    Task<ReviewSummary> GetSummaryAsync(int productId, CancellationToken ct = default);
    Task<Review> CreateReviewAsync(Review review, CancellationToken ct = default);
    Task<Review> UpdateReviewAsync(Review review, CancellationToken ct = default);
    Task DeleteReviewAsync(int reviewId, string userId, CancellationToken ct = default);
    Task ToggleLikeAsync(int reviewId, string userId, CancellationToken ct = default);
}
