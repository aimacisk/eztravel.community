using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Interfaces.Repositories;
using EzTravel.Community.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace EzTravel.Community.Infrastructure.Repositories;

public class ReviewLikeRepository : IReviewLikeRepository
{
    private readonly AppDbContext _db;

    public ReviewLikeRepository(AppDbContext db) => _db = db;

    public async Task<ReviewLike?> GetAsync(int reviewId, string userId, CancellationToken ct = default)
        => await _db.ReviewLikes.FirstOrDefaultAsync(l => l.ReviewId == reviewId && l.UserId == userId, ct);

    public async Task AddAsync(ReviewLike like, CancellationToken ct = default)
    {
        _db.ReviewLikes.Add(like);
        await _db.SaveChangesAsync(ct);
    }

    public async Task DeleteAsync(int reviewId, string userId, CancellationToken ct = default)
    {
        var like = await GetAsync(reviewId, userId, ct);
        if (like != null)
        {
            _db.ReviewLikes.Remove(like);
            await _db.SaveChangesAsync(ct);
        }
    }
}
