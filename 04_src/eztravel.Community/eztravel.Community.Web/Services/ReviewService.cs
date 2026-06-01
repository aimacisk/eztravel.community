using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Interfaces.Repositories;
using EzTravel.Community.Core.Interfaces.Services;
using EzTravel.Community.Core.Models;

namespace EzTravel.Community.Web.Services;

public class ReviewService : IReviewService
{
    private readonly IReviewRepository _reviews;
    private readonly IReviewLikeRepository _likes;

    public ReviewService(IReviewRepository reviews, IReviewLikeRepository likes)
    {
        _reviews = reviews;
        _likes = likes;
    }

    public Task<ReviewListResult> GetReviewsAsync(ReviewListQuery query, CancellationToken ct = default)
        => _reviews.ListAsync(query, ct);

    public Task<ReviewSummary> GetSummaryAsync(int productId, CancellationToken ct = default)
        => _reviews.GetSummaryAsync(productId, ct);

    public async Task<Review> CreateReviewAsync(Review review, CancellationToken ct = default)
    {
        await _reviews.AddAsync(review, ct);
        return review;
    }

    public async Task<Review> UpdateReviewAsync(Review review, CancellationToken ct = default)
    {
        await _reviews.UpdateAsync(review, ct);
        return review;
    }

    public Task DeleteReviewAsync(int reviewId, string userId, CancellationToken ct = default)
        => _reviews.DeleteAsync(reviewId, ct);

    public async Task ToggleLikeAsync(int reviewId, string userId, CancellationToken ct = default)
    {
        var existing = await _likes.GetAsync(reviewId, userId, ct);
        if (existing != null)
            await _likes.DeleteAsync(reviewId, userId, ct);
        else
            await _likes.AddAsync(new ReviewLike { ReviewId = reviewId, UserId = userId }, ct);
    }
}
