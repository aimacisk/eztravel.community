using EzTravel.Community.Core.Entities;

namespace EzTravel.Community.Core.Interfaces.Repositories;

public interface IReviewLikeRepository
{
    Task<ReviewLike?> GetAsync(int reviewId, string userId, CancellationToken ct = default);
    Task AddAsync(ReviewLike like, CancellationToken ct = default);
    Task DeleteAsync(int reviewId, string userId, CancellationToken ct = default);
}
