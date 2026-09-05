@Tags(['live'])
library;

/// Exercises the inventory data layer (DTO parsing + Dio + AuthInterceptor)
/// against a running backend. Skipped unless `LIVE_BASE_URL` is set:
///
///   flutter test test/live/inventory_live_test.dart --run-skipped \
///     --dart-define=LIVE_BASE_URL=http://127.0.0.1:4000/api
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/pantry/data/datasources/pantry_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

const _baseUrl = String.fromEnvironment('LIVE_BASE_URL');

class _MemStore implements SecureStore {
  String? _access;
  String? _refresh;
  @override
  Future<String?> readAccessToken() async => _access;
  @override
  Future<String?> readRefreshToken() async => _refresh;
  @override
  Future<void> writeTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    _access = accessToken;
    _refresh = refreshToken;
  }

  @override
  Future<void> clear() async {
    _access = null;
    _refresh = null;
  }
}

void main() {
  if (_baseUrl.isEmpty) {
    test('live inventory (skipped: set --dart-define=LIVE_BASE_URL)', () {},
        skip: true);
    return;
  }

  late PantryRepositoryImpl pantry;

  setUp(() async {
    final store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    final api = DioApiClient(dio);
    final auth = AuthRepositoryImpl(AuthRemoteDataSource(api), store);

    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final phone = '+8493${tail.substring(tail.length - 8)}';
    const password = 'secret12345';
    await auth.register(phone: phone, password: password, name: 'Inventory Live');
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: $f'), (_) {});

    pantry = PantryRepositoryImpl(PantryRemoteDataSource(api));
  });

  Future<PantryItem> addBatch({
    String name = 'Ức gà live',
    double quantity = 300,
    StorageTier tier = StorageTier.fridge,
  }) async {
    final res = await pantry.add(
      PantryItemDraft(
        name: name,
        quantity: quantity,
        unit: MeasurementUnit.gram,
        storageTier: tier,
        expiryDate: DateTime.now().toUtc().add(const Duration(days: 5)),
      ),
    );
    return res.fold((f) => fail('add failed: $f'), (i) => i);
  }

  test('add() creates a batch and list() returns it', () async {
    final created = await addBatch();
    expect(created.id, isNotEmpty);
    expect(created.quantity, 300);
    expect(created.unit, MeasurementUnit.gram);
    expect(created.storageTier, StorageTier.fridge);

    final res = await pantry.list();
    final page = res.fold((f) => fail('list failed: $f'), (p) => p);
    expect(page.items.any((i) => i.id == created.id), isTrue);
  });

  test('consume() reduces quantity; consuming it all marks used', () async {
    final created = await addBatch(quantity: 200);

    final partial = await pantry.consume(created.id, quantityUsed: 50);
    final afterPartial = partial.fold((f) => fail('consume failed: $f'), (i) => i);
    expect(afterPartial.quantity, 150);
    expect(afterPartial.status, PantryItemStatus.active);

    final full = await pantry.consume(created.id, quantityUsed: 150);
    final afterFull = full.fold((f) => fail('consume failed: $f'), (i) => i);
    expect(afterFull.quantity, 0);
    expect(afterFull.status, PantryItemStatus.used);
  });

  test('update() moves the batch to a different storage tier', () async {
    final created = await addBatch(tier: StorageTier.fridge);
    expect(created.storageTier, StorageTier.fridge);

    final res = await pantry.update(
      created.id,
      PantryItemDraft.fromItem(created).copyWith(storageTier: StorageTier.freezer),
    );
    final updated = res.fold((f) => fail('update failed: $f'), (i) => i);
    expect(updated.storageTier, StorageTier.freezer);
  });

  test('delete() archives the batch out of the active list', () async {
    final created = await addBatch();

    final del = await pantry.delete(created.id);
    expect(del.isRight(), isTrue);

    final res = await pantry.list();
    final page = res.fold((f) => fail('list failed: $f'), (p) => p);
    expect(page.items.any((i) => i.id == created.id), isFalse);
  });
}
