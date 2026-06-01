using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Enums;
using EzTravel.Community.Core.Interfaces.Repositories;
using EzTravel.Community.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace EzTravel.Community.Infrastructure.Repositories;

public class ProductRepository : IProductRepository
{
    private readonly AppDbContext _db;

    public ProductRepository(AppDbContext db) => _db = db;

    public async Task<Product?> GetByIdAsync(int id, CancellationToken ct = default)
        => await _db.Products.FirstOrDefaultAsync(p => p.Id == id && !p.IsDeleted, ct);

    public async Task<IReadOnlyList<Product>> GetByCategoryAsync(ProductCategory category, CancellationToken ct = default)
        => await _db.Products.Where(p => p.Category == category && !p.IsDeleted).ToListAsync(ct);
}
