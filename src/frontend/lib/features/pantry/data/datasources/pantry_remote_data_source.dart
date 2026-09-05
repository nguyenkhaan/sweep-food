import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/utils/idempotency.dart';
import 'package:sweepfood/features/pantry/data/models/pantry_item_dto.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/features/pantry/domain/repositories/pantry_repository.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// Talks to `/inventory/batches`. Throws on failure — the repository catches
/// and maps. See `docs/api-contract.md` §10.
class PantryRemoteDataSource {
  PantryRemoteDataSource(this._api);

  final ApiClient _api;

  /// The backend has no `sort` param and only two meaningful statuses to
  /// query by (`ACTIVE`/`DEPLETED`) — [PantryItemStatus.expired] has no
  /// backend equivalent (expiry is a computed read-time property, not a
  /// stored status), so it falls back to `ACTIVE`. `per_page` is capped at
  /// the backend's max (100); with more active batches than that, the tail is
  /// silently not fetched — acceptable for MVP.
  Future<List<PantryItemDto>> list({
    StorageTier? tier,
    required PantryItemStatus status,
    required PantrySort sort,
    required int page,
  }) async {
    final json = await _api.get(
      ApiPaths.inventoryBatches,
      query: {
        'status': status == PantryItemStatus.used ? 'DEPLETED' : 'ACTIVE',
        if (tier != null) 'storage_mode': tier.backendWire,
        'page': page,
        'per_page': 100,
      },
    );
    final items = (json as Map<String, dynamic>)['items'] as List<dynamic>;
    return items
        .map((e) => PantryItemDto.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<PantryItemDto> add(PantryItemDraft draft) async {
    final json = await _api.post(
      ApiPaths.inventoryBatches,
      body: draftToBody(draft),
      headers: _idempotencyHeaders(),
    );
    return PantryItemDto.fromJson(json as Map<String, dynamic>);
  }

  /// The backend has no bulk-create endpoint — each row is posted one at a
  /// time (sequentially, so a partial failure doesn't fan out into a burst of
  /// concurrent retries).
  Future<List<PantryItemDto>> addBatch(List<PantryItemDraft> drafts) async {
    final results = <PantryItemDto>[];
    for (final draft in drafts) {
      results.add(await add(draft));
    }
    return results;
  }

  /// `PATCH` only covers metadata (note/dates/cost) — quantity and identity
  /// are immutable, and a storage-tier change needs the dedicated `/move`
  /// ledger endpoint. Both are issued here since the shared edit form doesn't
  /// distinguish "edited metadata" from "moved shelf"; moving to the same
  /// tier is a harmless no-op ledger entry.
  Future<PantryItemDto> update(String id, PantryItemDraft draft) async {
    await _api.patch(
      ApiPaths.inventoryBatch(id),
      body: {
        if (draft.packedDate != null)
          'packaged_at': draft.packedDate!.toUtc().toIso8601String(),
        if (draft.expiryDate != null)
          'expires_at': draft.expiryDate!.toUtc().toIso8601String(),
        if (draft.priceVnd != null) 'unit_cost': draft.priceVnd,
        'reason': 'Cập nhật từ ứng dụng',
      },
      headers: _idempotencyHeaders(),
    );
    final json = await _api.post(
      ApiPaths.inventoryBatchMove(id),
      body: {
        'storage_mode': draft.storageTier.backendWire,
        'reason': 'Cập nhật từ ứng dụng',
      },
      headers: _idempotencyHeaders(),
    );
    return PantryItemDto.fromJson(json as Map<String, dynamic>);
  }

  Future<void> delete(String id) => _api.delete(
        ApiPaths.inventoryBatch(id),
        headers: {
          'Idempotency-Key': Idempotency.newKey(),
          // HTTP header values must be ASCII — unlike JSON body fields, this
          // can't carry Vietnamese text (a non-ASCII header throws at the Dio
          // layer, surfacing as an unmapped UnknownFailure).
          'X-Reason': 'User deleted from inventory',
        },
      );

  Future<PantryItemDto> consume(String id, double quantityUsed) async {
    final json = await _api.post(
      ApiPaths.inventoryBatchConsume(id),
      body: {'quantity': quantityUsed, 'reason': 'Người dùng ghi nhận đã dùng'},
      headers: _idempotencyHeaders(),
    );
    return PantryItemDto.fromJson(json as Map<String, dynamic>);
  }

  Map<String, String> _idempotencyHeaders() =>
      {'Idempotency-Key': Idempotency.newKey()};

  static Map<String, dynamic> draftToBody(PantryItemDraft d) => {
        if (d.ingredientId != null)
          'master_ingredient_id': d.ingredientId
        else
          'custom_name': d.name.trim(),
        'quantity': d.quantity,
        'unit': d.unit.backendWire,
        'storage_mode': d.storageTier.backendWire,
        if (d.packedDate != null)
          'packaged_at': d.packedDate!.toUtc().toIso8601String(),
        if (d.expiryDate != null)
          'expires_at': d.expiryDate!.toUtc().toIso8601String(),
        if (d.priceVnd != null) 'unit_cost': d.priceVnd,
      };
}
