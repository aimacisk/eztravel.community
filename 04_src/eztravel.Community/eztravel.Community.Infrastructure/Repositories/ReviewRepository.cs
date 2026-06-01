using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Interfaces.Repositories;
using EzTravel.Community.Core.Models;
using EzTravel.Community.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace EzTravel.Community.Infrastructure.Repositories;

public class ReviewRepository : IReviewRepository
{
    private readonly AppDbContext _db;

    public ReviewRepository(AppDbContext db) => _db = db;

    public async Task<Review?> GetByIdAsync(int id, CancellationToken ct = default)
        => await _db.Reviews.Include(r => r.User).FirstOrDefaultAsync(r => r.Id == id && !r.IsDeleted, ct);

    public async Task<ReviewListResult> ListAsync(ReviewListQuery query, CancellationToken ct = default)
    {
        var q = _db.Reviews.Where(r => r.ProductId == query.ProductId && !r.IsDeleted);

        if (query.Stars.HasValue)
            q = q.Where(r => r.Rating == query.Stars.Value);

        if (query.HasPhoto == true)
            q = q.Where(r => r.PhotoUrl != null);

        q = query.Sort == "helpful"
            ? q.OrderByDescending(r => r.HelpfulCount)
            : q.OrderByDescending(r => r.CreatedAt);

        var total = await q.CountAsync(ct);
        var items = await q.Skip((query.Page - 1) * query.PageSize).Take(query.PageSize).ToListAsync(ct);

        return new ReviewListResult
        {
            TotalCount = total,
            HasNextPage = query.Page * query.PageSize < total,
            Items = items
        };
    }

    public async Task<ReviewSummary> GetSummaryAsync(int productId, CancellationToken ct = default)
    {
        var reviews = await _db.Reviews.Where(r => r.ProductId == productId && !r.IsDeleted).ToListAsync(ct);
        return new ReviewSummary
        {
            ProductId = productId,
            TotalReviews = reviews.Count,
            AverageRating = reviews.Count > 0 ? reviews.Average(r => r.Rating) : 0,
            FiveStarCount = reviews.Count(r => r.Rating == 5),
            FourStarCount = reviews.Count(r => r.Rating == 4),
            ThreeStarCount = reviews.Count(r => r.Rating == 3),
            TwoStarCount = reviews.Count(r => r.Rating == 2),
            OneStarCount = reviews.Count(r => r.Rating == 1),
            PhotoReviewCount = reviews.Count(r => r.PhotoUrl != null)
        };
    }

    public async Task AddAsync(Review review, CancellationToken ct = default)
    {
        _db.Reviews.Add(review);
        await _db.SaveChangesAsync(ct);
    }

    public async Task UpdateAsync(Review review, CancellationToken ct = default)
    {
        review.UpdatedAt = DateTime.UtcNow;
        _db.Reviews.Update(review);
        await _db.SaveChangesAsync(ct);
    }

    public async Task DeleteAsync(int id, CancellationToken ct = default)
    {
        var review = await _db.Reviews.FindAsync(new object[] { id }, ct);
        if (review != null)
        {
            review.IsDeleted = true;
            await _db.SaveChangesAsync(ct);
        }
    }
}
