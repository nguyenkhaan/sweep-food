import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/catalog/data/datasources/ingredient_remote_data_source.dart';
import 'package:sweepfood/features/catalog/data/repositories/ingredient_repository_impl.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

class _MockApiClient extends Mock implements ApiClient {}

Map<String, dynamic> _listItem({
  required String id,
  required String name,
  required String categoryName,
  required String unit,
  String? storageMode,
  List<String> aliases = const [],
}) =>
    {
      'id': id,
      'name': name,
      'category': {'id': 'cat-$id', 'name': categoryName},
      'default_unit': unit,
      'default_storage_mode': storageMode,
      'aliases': aliases,
    };

void main() {
  late _MockApiClient api;
  late IngredientRepositoryImpl repo;

  setUp(() {
    api = _MockApiClient();
    repo = IngredientRepositoryImpl(IngredientRemoteDataSource(api));
  });

  group('search()', () {
    test('sends q= and maps the paged backend list to entities', () async {
      when(() => api.get(ApiPaths.ingredients, query: any(named: 'query')))
          .thenAnswer((_) async => {
                'items': [
                  _listItem(
                    id: 'i1',
                    name: 'Chicken breast',
                    categoryName: 'Proteins',
                    unit: 'GRAM',
                    aliases: ['Ức gà'],
                  ),
                  _listItem(
                    id: 'i2',
                    name: 'Fresh milk',
                    categoryName: 'Dairy',
                    unit: 'ML',
                  ),
                ],
                'total': 2,
                'page': 1,
                'per_page': 20,
              });

      final res = await repo.search('ch');

      final list = res.fold((f) => fail('expected Right, got $f'), (l) => l);
      expect(list, hasLength(2));
      expect(list.first.name, 'Chicken breast');
      expect(list.first.category, 'Proteins');
      expect(list.first.defaultUnit, MeasurementUnit.gram);
      expect(list[1].defaultUnit, MeasurementUnit.milliliter);
      expect(list.first.referenceShelfLifeDays, isNull);

      final query = verify(
        () => api.get(ApiPaths.ingredients, query: captureAny(named: 'query')),
      ).captured.single as Map<String, dynamic>;
      expect(query, {'q': 'ch'});
    });

    test('omits the query param when the term is blank', () async {
      when(() => api.get(ApiPaths.ingredients, query: any(named: 'query')))
          .thenAnswer((_) async => {'items': <dynamic>[]});

      await repo.search('   ');

      final query = verify(
        () => api.get(ApiPaths.ingredients, query: captureAny(named: 'query')),
      ).captured.single as Map<String, dynamic>;
      expect(query, isEmpty);
    });

    test('returns a Failure when the request throws', () async {
      when(() => api.get(ApiPaths.ingredients, query: any(named: 'query')))
          .thenThrow(Exception('boom'));

      final res = await repo.search('x');

      expect(res.isLeft(), isTrue);
    });
  });

  group('byId()', () {
    test('maps detail nutrition and flattens shelf-life by storage mode',
        () async {
      when(() => api.get(ApiPaths.ingredient('i1'))).thenAnswer(
        (_) async => {
          ..._listItem(
            id: 'i1',
            name: 'Fresh milk',
            categoryName: 'Dairy',
            unit: 'ML',
            storageMode: 'REFRIGERATED',
          ),
          'description': 'Pasteurized cow milk.',
          'default_media_url': null,
          'nutrition': {
            'calories': 61.0,
            'protein_g': 3.2,
            'fat_g': 3.3,
            'carbs_g': 4.8,
            'sugar_g': 4.8,
            'sodium_mg': 43.0,
            'other_nutrients': {'calcium_mg': 113.0},
          },
          'shelf_life_rules': [
            {
              'scope': 'INGREDIENT',
              'storage_mode': 'FROZEN',
              'min_days': 30,
              'max_days': 90,
              'default_days': 60,
            },
            {
              'scope': 'INGREDIENT',
              'storage_mode': 'REFRIGERATED',
              'min_days': 3,
              'max_days': 5,
              'default_days': 4,
            },
          ],
        },
      );

      final res = await repo.byId('i1');

      final ing = res.fold((f) => fail('expected Right, got $f'), (i) => i);
      expect(ing.defaultUnit, MeasurementUnit.milliliter);
      expect(ing.referenceShelfLifeDays, 4); // matches REFRIGERATED, not FROZEN
      expect(ing.nutritionPer100g, isNotNull);
      expect(ing.nutritionPer100g!.energyKcal, 61.0);
      expect(ing.nutritionPer100g!.lipidG, 3.3); // fat_g → lipidG
      expect(ing.nutritionPer100g!.carbG, 4.8); // carbs_g → carbG
    });

    test('tolerates decimal macros encoded as strings', () async {
      when(() => api.get(ApiPaths.ingredient('i2'))).thenAnswer(
        (_) async => {
          ..._listItem(
            id: 'i2',
            name: 'Rice',
            categoryName: 'Grains',
            unit: 'GRAM',
            storageMode: 'DRY_SHELF',
          ),
          'nutrition': {
            'calories': '130.000',
            'protein_g': '2.400',
            'fat_g': '0.300',
            'carbs_g': '28.700',
          },
          'shelf_life_rules': <dynamic>[],
        },
      );

      final res = await repo.byId('i2');
      final ing = res.fold((f) => fail('$f'), (i) => i);
      expect(ing.nutritionPer100g!.energyKcal, 130.0);
      expect(ing.referenceShelfLifeDays, isNull);
    });
  });
}
