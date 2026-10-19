import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/add_ingredient_controller.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

class _MockApiClient extends Mock implements ApiClient {}

Map<String, dynamic> _textResponse({
  String? name,
  String? masterId,
  double? quantity,
  String? unit,
}) => {
  'request_id': 'r1',
  'status': 'PARTIAL',
  'provider': 'SWEEP_FOOD_AI',
  'raw_text': 'x',
  'fields': {
    'ingredient_name': name,
    'raw_name': 'raw',
    'master_ingredient_id': masterId,
    'quantity': quantity,
    'unit': unit,
  },
  'confidence': <String, dynamic>{},
  'warnings': <String>[],
  'persisted': false,
};

void main() {
  late _MockApiClient api;
  late ProviderContainer container;

  AddIngredientController notifier() =>
      container.read(addIngredientControllerProvider(null).notifier);

  setUp(() {
    api = _MockApiClient();
    container = ProviderContainer(
      overrides: [apiClientProvider.overrideWithValue(api)],
    );
    addTearDown(container.dispose);
  });

  void stubMatch(Object response) {
    when(
      () => api.post(ApiPaths.extractionText, body: any(named: 'body')),
    ).thenAnswer((_) async => response);
  }

  group('matchTypedName()', () {
    test('links the catalog match, normalizes the name and fills an empty quantity', () async {
      stubMatch(
        _textResponse(
          name: 'Thịt ba chỉ',
          masterId: 'ing-7',
          quantity: 500,
          unit: 'GRAM',
        ),
      );
      notifier().setName('thịt ba rọi 500g');

      final changed = await notifier().matchTypedName();

      final draft = container.read(addIngredientControllerProvider(null));
      expect(changed, isTrue);
      expect(draft.name, 'Thịt ba chỉ');
      expect(draft.ingredientId, 'ing-7');
      expect(draft.quantity, 500);
      expect(draft.unit, MeasurementUnit.gram);
    });

    test('keeps a quantity the user already entered', () async {
      stubMatch(
        _textResponse(
          name: 'Thịt ba chỉ',
          masterId: 'ing-7',
          quantity: 500,
          unit: 'GRAM',
        ),
      );
      notifier()
        ..setName('thịt ba rọi 500g')
        ..setQuantity(2)
        ..setUnit(MeasurementUnit.kilogram);

      await notifier().matchTypedName();

      final draft = container.read(addIngredientControllerProvider(null));
      expect(draft.quantity, 2);
      expect(draft.unit, MeasurementUnit.kilogram);
      expect(draft.ingredientId, 'ing-7');
    });

    test('leaves the draft untouched when the text has no catalog match', () async {
      stubMatch(_textResponse(name: 'Món lạ'));
      notifier().setName('món lạ');

      final changed = await notifier().matchTypedName();

      final draft = container.read(addIngredientControllerProvider(null));
      expect(changed, isFalse);
      expect(draft.name, 'món lạ');
      expect(draft.ingredientId, isNull);
    });

    test('swallows backend failures so manual entry keeps working', () async {
      when(
        () => api.post(ApiPaths.extractionText, body: any(named: 'body')),
      ).thenThrow(Exception('offline'));
      notifier().setName('cà chua');

      expect(await notifier().matchTypedName(), isFalse);
      expect(
        container.read(addIngredientControllerProvider(null)).name,
        'cà chua',
      );
    });

    test('does not call the parser for an already matched item', () async {
      notifier().setName('cà chua');
      stubMatch(_textResponse(name: 'Cà chua', masterId: 'ing-1'));
      await notifier().matchTypedName();
      clearInteractions(api);

      expect(await notifier().matchTypedName(), isFalse);
      verifyNever(
        () => api.post(ApiPaths.extractionText, body: any(named: 'body')),
      );
    });
  });

  group('freshness bookkeeping', () {
    final estimate = FreshnessEstimate(
      answers: const {'appearance': 'fresh'},
      expiresAt: DateTime.utc(2026, 9, 3),
    );

    test('a manual date and a FreshCheck estimate are mutually exclusive', () {
      notifier().setExpiry(null, estimate);
      expect(
        container.read(addIngredientControllerProvider(null)).freshness,
        estimate,
      );

      notifier().setExpiry(DateTime(2026, 9, 10), null);
      final draft = container.read(addIngredientControllerProvider(null));
      expect(draft.expiryDate, DateTime(2026, 9, 10));
      expect(draft.freshness, isNull);
    });

    test('editing the name detaches the catalog match and the estimate', () async {
      stubMatch(_textResponse(name: 'Cà chua', masterId: 'ing-1'));
      notifier().setName('cà chua');
      await notifier().matchTypedName();
      notifier().setExpiry(null, estimate);

      notifier().setName('cà rốt');

      final draft = container.read(addIngredientControllerProvider(null));
      expect(draft.ingredientId, isNull);
      expect(draft.freshness, isNull);
    });

    test('changing the storage tier discards an estimate made for another tier', () {
      notifier().setExpiry(null, estimate);

      notifier().setTier(StorageTier.fridge); // unchanged
      expect(
        container.read(addIngredientControllerProvider(null)).freshness,
        estimate,
      );

      notifier().setTier(StorageTier.freezer);
      expect(
        container.read(addIngredientControllerProvider(null)).freshness,
        isNull,
      );
    });
  });
}
