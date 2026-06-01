using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Enums;
using EzTravel.Community.Infrastructure.Data;
using EzTravel.Community.Web.Models.ViewModels;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace EzTravel.Community.Web.Controllers;

[Route("product")]
public class ProductController : Controller
{
    private readonly AppDbContext _db;

    public ProductController(AppDbContext db)
    {
        _db = db;
    }

    [HttpGet("detail/{id:int}")]
    public async Task<IActionResult> Detail(int id)
    {
        var product = await _db.Products
            .Include(p => p.Reviews.Where(r => !r.IsDeleted))
            .FirstOrDefaultAsync(p => p.Id == id && !p.IsDeleted);

        if (product is null) return NotFound();

        var vm = new ProductDetailViewModel
        {
            Id = product.Id,
            Name = product.Name,
            Description = product.Description,
            Category = product.Category,
            ImageUrl = product.ImageUrl,
            ReviewCount = product.Reviews.Count,
            AverageRating = product.Reviews.Count > 0
                ? Math.Round(product.Reviews.Average(r => (double)r.Rating), 1)
                : 0
        };

        return View(vm);
    }
}
