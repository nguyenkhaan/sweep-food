import 'package:frontend/core/network/api_client.dart';
import 'package:frontend/core/network/api_paths.dart';
import 'package:frontend/features/pantry/data/models/pantry_item_dto.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:frontend/features/pantry/domain/repositories/pantry_repository.dart';
import 'package:frontend/shared/domain/storage_tier.dart';

/// Talks to `/pantry/*`. Throws on failure — the repository catches and maps.
class PantryRemoteDataSource {
  PantryRemoteDataSource(this._api);

  final ApiClient _api;

  Future<List<PantryItemDto>> list({
    StorageTier? tier,
    required PantryItemStatus status,
    required PantrySort sort,
    required int page,
  }) async {
    final json = await _api.get(
      ApiPaths.pantryItems,
      query: {
        if (tier != null) 'tier': tier.wire,
        'status': status.wire,
        'sort': sort.name,
        'page': page,
      },
    );
    final items = (json is Map ? json['items'] : json) as List<dynamic>;
    return items
        .map((e) => PantryItemDto.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<PantrySummaryDto> summary() async {
    final json = await _api.get(ApiPaths.pantrySummary);
    return PantrySummaryDto.fromJson(json as Map<String, dynamic>);
  }

  Future<PantryItemDto> add(PantryItemDraft draft) async {
    final json = await _api.post(ApiPaths.pantryItems, body: draftToBody(draft));
    return PantryItemDto.fromJson(json as Map<String, dynamic>);
  }

  Future<List<PantryItemDto>> addBatch(List<PantryItemDraft> drafts) async {
    final json = await _api.post(
      ApiPaths.pantryItemsBatch,
      body: {'items': drafts.map(draftToBody).toList()},
    );
    final items = (json is Map ? json['items'] : json) as List<dynamic>;
    return items
        .map((e) => PantryItemDto.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<PantryItemDto> update(String id, PantryItemDraft draft) async {
    final json = await _api.patch(
      ApiPaths.pantryItem(id),
      body: draftToBody(draft),
    );
    return PantryItemDto.fromJson(json as Map<String, dynamic>);
  }

  Future<void> delete(String id) => _api.delete(ApiPaths.pantryItem(id));

  Future<PantryItemDto> consume(String id, double quantityUsed) async {
    final json = await _api.post(
      ApiPaths.pantryItemConsume(id),
      body: {'quantity': quantityUsed},
    );
    return PantryItemDto.fromJson(json as Map<String, dynamic>);
  }

  static Map<String, dynamic> draftToBody(PantryItemDraft d) => {
        'name': d.name.trim(),
        'category': d.category,
        'quantity': d.quantity,
        'unit': d.unit.wire,
        'storage_tier': d.storageTier.wire,
        'source': d.source.wire,
        if (d.ingredientId != null) 'ingredient_id': d.ingredientId,
        if (d.packedDate != null)
          'packed_date': d.packedDate!.toIso8601String(),
        if (d.expiryDate != null)
          'expiry_date': d.expiryDate!.toIso8601String(),
        if (d.referenceShelfLifeDays != null)
          'reference_shelf_life_days': d.referenceShelfLifeDays,
        if (d.priceVnd != null) 'price_vnd': d.priceVnd,
      };
}
