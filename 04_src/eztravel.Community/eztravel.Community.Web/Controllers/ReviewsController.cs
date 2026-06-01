using System.Security.Claims;
using EzTravel.Community.Core.Entities;
using EzTravel.Community.Infrastructure.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace EzTravel.Community.Web.Controllers;

[ApiController]
[Route("api")]
public class ReviewsController : ControllerBase
{
    private readonly AppDbContext _db;
    private const int RateLimitHours = 24;
    private const int MinBodyLength = 10;
    private const int MaxBodyLength = 2000;

    public ReviewsController(AppDbContext db)
    {
        _db = db;
    }

    [HttpGet("products/{productId:int}/reviews")]
    public async Task<IActionResult> List(int productId, [FromQuery] int? stars, [FromQuery] bool? hasPhoto, [FromQuery] string? sort, [FromQuery] int page = 1, [FromQuery] int pageSize = 20)
    {
        var q = _db.Reviews.AsNoTracking().Where(r => r.ProductId == productId && !r.IsDeleted);

        if (stars.HasValue) q = q.Where(r => r.Rating == stars.Value);
        if (hasPhoto == true) q = q.Where(r => r.PhotoUrl != null);

        q = sort switch
        {
            "newest" => q.OrderByDescending(r => r.CreatedAt),
            "most-helpful" => q.OrderByDescending(r => r.HelpfulCount).ThenByDescending(r => r.CreatedAt),
            _ => q.OrderByDescending(r => r.CreatedAt)
        };

        var total = await q.CountAsync();
        var items = await q.Skip((page - 1) * pageSize).Take(pageSize).ToListAsync();

        return Ok(new { items, total, page, pageSize });
    }

    [Authorize]
    [HttpPost("products/{productId:int}/reviews")]
    public async Task<IActionResult> Create(int productId, [FromBody] CreateReviewDto dto)
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
        if (userId is null) return Unauthorized();

        if (dto.Rating < 1 || dto.Rating > 5) return BadRequest(new { error = "rating must be 1-5" });
        if (string.IsNullOrWhiteSpace(dto.Body) || dto.Body.Length < MinBodyLength || dto.Body.Length > MaxBodyLength)
            return BadRequest(new { error = $"body length must be {MinBodyLength}-{MaxBodyLength}" });

        var since = DateTime.UtcNow.AddHours(-RateLimitHours);
        var recent = await _db.Reviews.AnyAsync(r => r.UserId == userId && r.ProductId == productId && r.CreatedAt > since && !r.IsDeleted);
        if (recent) return Conflict(new { error = $"only one review per product per {RateLimitHours}h" });

        var body = System.Net.WebUtility.HtmlEncode(dto.Body.Trim());
        var review = new Review
        {
            ProductId = productId,
            UserId = userId,
            Rating = dto.Rating,
            Title = string.IsNullOrWhiteSpace(dto.Title) ? null : System.Net.WebUtility.HtmlEncode(dto.Title!.Trim()),
            Body = body,
            PhotoUrl = dto.PhotoUrl,
            ParentReviewId = dto.ParentReviewId
        };
        _db.Reviews.Add(review);
        await _db.SaveChangesAsync();

        return CreatedAtAction(nameof(List), new { productId }, review);
    }

    [Authorize]
    [HttpPatch("reviews/{id:int}")]
    public async Task<IActionResult> Edit(int id, [FromBody] EditReviewDto dto)
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
        var review = await _db.Reviews.FirstOrDefaultAsync(r => r.Id == id && !r.IsDeleted);
        if (review is null) return NotFound();
        if (review.UserId != userId) return Forbid();
        if (review.CreatedAt < DateTime.UtcNow.AddHours(-24)) return Conflict(new { error = "edit window expired (24h)" });

        if (dto.Body is not null)
        {
            if (dto.Body.Length < MinBodyLength || dto.Body.Length > MaxBodyLength)
                return BadRequest(new { error = $"body length must be {MinBodyLength}-{MaxBodyLength}" });
            review.Body = System.Net.WebUtility.HtmlEncode(dto.Body.Trim());
        }
        if (dto.Rating.HasValue)
        {
            if (dto.Rating.Value < 1 || dto.Rating.Value > 5) return BadRequest();
            review.Rating = dto.Rating.Value;
        }
        review.UpdatedAt = DateTime.UtcNow;
        await _db.SaveChangesAsync();
        return Ok(review);
    }

    [Authorize]
    [HttpDelete("reviews/{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
        var review = await _db.Reviews.FirstOrDefaultAsync(r => r.Id == id && !r.IsDeleted);
        if (review is null) return NotFound();
        if (review.UserId != userId) return Forbid();

        review.IsDeleted = true;
        review.UpdatedAt = DateTime.UtcNow;
        await _db.SaveChangesAsync();
        return NoContent();
    }

    [Authorize]
    [HttpPost("reviews/{id:int}/like")]
    public async Task<IActionResult> Like(int id)
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
        if (userId is null) return Unauthorized();

        var exists = await _db.ReviewLikes.AnyAsync(l => l.ReviewId == id && l.UserId == userId);
        if (exists) return Conflict(new { error = "already liked" });

        var review = await _db.Reviews.FirstOrDefaultAsync(r => r.Id == id && !r.IsDeleted);
        if (review is null) return NotFound();

        _db.ReviewLikes.Add(new ReviewLike { ReviewId = id, UserId = userId });
        review.HelpfulCount++;
        await _db.SaveChangesAsync();
        return Ok(new { helpfulCount = review.HelpfulCount });
    }

    [Authorize]
    [HttpPost("reviews/{id:int}/reply")]
    public async Task<IActionResult> Reply(int id, [FromBody] CreateReviewDto dto)
    {
        var parent = await _db.Reviews.AsNoTracking().FirstOrDefaultAsync(r => r.Id == id && !r.IsDeleted);
        if (parent is null) return NotFound();
        dto.ParentReviewId = id;
        return await Create(parent.ProductId, dto);
    }
}

public record CreateReviewDto
{
    public int Rating { get; set; }
    public string? Title { get; set; }
    public string Body { get; set; } = string.Empty;
    public string? PhotoUrl { get; set; }
    public int? ParentReviewId { get; set; }
}

public record EditReviewDto
{
    public int? Rating { get; set; }
    public string? Body { get; set; }
}
