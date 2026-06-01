using EzTravel.Community.Core.Entities;
using EzTravel.Community.Core.Enums;

namespace EzTravel.Community.Core.Interfaces.Repositories;

public interface IProductRepository
{
    Task<Product?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<Product>> GetByCategoryAsync(ProductCategory category, CancellationToken ct = default);
}
