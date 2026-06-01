using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Models;

namespace EzTravel.Community.Core.Interfaces.Repositories;

public interface IReviewRepository
{
    Task<Review?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<ReviewListResult> ListAsync(ReviewListQuery query, CancellationToken ct = default);
    Task<ReviewSummary> GetSummaryAsync(int productId, CancellationToken ct = default);
    Task AddAsync(Review review, CancellationToken ct = default);
    Task UpdateAsync(Review review, CancellationToken ct = default);
    Task DeleteAsync(int id, CancellationToken ct = default);
}
