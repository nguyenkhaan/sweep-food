import 'package:frontend/core/network/api_result.dart';
import 'package:frontend/core/network/network_providers.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/pantry/data/datasources/pantry_remote_data_source.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_summary.dart';
import 'package:frontend/features/pantry/domain/repositories/pantry_repository.dart';
import 'package:frontend/shared/domain/paginated.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'pantry_repository_impl.g.dart';

@Riverpod(keepAlive: true)
PantryRepository pantryRepository(Ref ref) => PantryRepositoryImpl(
      PantryRemoteDataSource(ref.watch(apiClientProvider)),
    );

class PantryRepositoryImpl implements PantryRepository {
  PantryRepositoryImpl(this._remote);

  final PantryRemoteDataSource _remote;

  @override
  Future<Result<Paginated<PantryItem>>> list({
    StorageTier? tier,
    PantryItemStatus status = PantryItemStatus.active,
    PantrySort sort = PantrySort.priority,
    int page = 1,
  }) =>
      runGuarded(() async {
        final dtos = await _remote.list(
          tier: tier,
          status: status,
          sort: sort,
          page: page,
        );
        return Paginated.single([for (final d in dtos) d.toEntity()]);
      });

  @override
  Future<Result<PantrySummary>> summary() =>
      runGuarded(() async => (await _remote.summary()).toEntity());

  @override
  Future<Result<PantryItem>> add(PantryItemDraft draft) =>
      runGuarded(() async => (await _remote.add(draft)).toEntity());

  @override
  Future<Result<List<PantryItem>>> addBatch(List<PantryItemDraft> drafts) =>
      runGuarded(() async {
        final dtos = await _remote.addBatch(drafts);
        return [for (final d in dtos) d.toEntity()];
      });

  @override
  Future<Result<PantryItem>> update(String id, PantryItemDraft draft) =>
      runGuarded(() async => (await _remote.update(id, draft)).toEntity());

  @override
  Future<Result<void>> delete(String id) => guardVoid(() => _remote.delete(id));

  @override
  Future<Result<PantryItem>> consume(String id, {required double quantityUsed}) =>
      runGuarded(() async => (await _remote.consume(id, quantityUsed)).toEntity());
}
