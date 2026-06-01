using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Enums;

namespace EzTravel.Community.Core.Interfaces.Services;

public interface IProductService
{
    Task<Product?> GetProductAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<Product>> GetProductsByCategoryAsync(ProductCategory category, CancellationToken ct = default);
}
