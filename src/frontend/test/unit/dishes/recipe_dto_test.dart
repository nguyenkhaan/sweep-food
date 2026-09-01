import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/dishes/data/datasources/dish_remote_data_source.dart';
import 'package:sweepfood/features/dishes/data/models/recipe_dto.dart';
import 'package:sweepfood/features/dishes/data/repositories/dish_repository_impl.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

class _MockApiClient extends Mock implements ApiClient {}

Map<String, dynamic> _recipeJson({Object servings = 2.0}) => {
      'id': 'r1',
      'name': 'Grilled chicken breast',
      'description': 'Simple high-protein chicken breast.',
      'media_url': null,
      'default_servings': 2.0,
      'estimated_cooking_minutes': 25,
      'estimated_cost': 75000.0,
      'tags': {
        'values': ['high-protein'],
      },
      'servings': servings,
      'instructions': {
        'steps': ['Season chicken', 'Grill until cooked'],
      },
      'nutrition': {
        'calories': 330.0,
        'protein_g': 62.0,
        'fat_g': 7.2,
        'carbs_g': 0.0,
        'sugar_g': 0.0,
        'other_nutrients': <String, dynamic>{},
      },
      'ingredients': [
        {
          'recipe_ingredient_id': 'ri1',
          'master_ingredient_id': 'mi1',
          'name': 'Chicken breast',
          'required_quantity': 300.0,
          'unit': 'GRAM',
          'is_optional': false,
          'preparation_note': null,
        },
        {
          'recipe_ingredient_id': 'ri2',
          'master_ingredient_id': 'mi2',
          'name': 'Olive oil',
          'required_quantity': 15.0,
          'unit': 'ML',
          'is_optional': true,
          'preparation_note': null,
        },
      ],
    };

void main() {
  group('RecipeDto.toEntity()', () {
    test('maps the backend recipe shape to a Dish', () {
      final dish = RecipeDto.fromJson(_recipeJson()).toEntity();

      expect(dish.id, 'r1');
      expect(dish.name, 'Grilled chicken breast');
      expect(dish.servings, 2);
      expect(dish.prepTimeMin, 0);
      expect(dish.cookTimeMin, 25);
      expect(dish.cuisine, '');
      expect(dish.difficulty, '');

      // nutrition arrives scaled to `servings` (a total) → divided back down.
      expect(dish.nutritionPerServing.energyKcal, 165.0); // 330 / 2
      expect(dish.nutritionPerServing.proteinG, 31.0); // 62 / 2
      expect(dish.nutritionPerServing.lipidG, closeTo(3.6, 1e-9)); // fat_g / 2
      expect(dish.nutritionPerServing.carbG, 0.0);

      // instructions.steps (list of strings) → ordered CookingSteps.
      expect(dish.steps.map((s) => s.order), [1, 2]);
      expect(dish.steps.first.text, 'Season chicken');
      expect(dish.steps.first.durationMin, isNull);
    });

    test('maps ingredients: unit via fromWire, isSeasoning from is_optional', () {
      final dish = RecipeDto.fromJson(_recipeJson()).toEntity();

      final chicken = dish.ingredients.firstWhere((i) => i.name == 'Chicken breast');
      expect(chicken.quantity, 300.0);
      expect(chicken.unit, MeasurementUnit.gram);
      expect(chicken.isSeasoning, isFalse);
      expect(chicken.availableInPantry, isFalse); // backend has no pantry join

      final oil = dish.ingredients.firstWhere((i) => i.name == 'Olive oil');
      expect(oil.unit, MeasurementUnit.milliliter);
      expect(oil.isSeasoning, isTrue); // is_optional → seasoning chip

      // mainIngredients excludes the optional one; it becomes a seasoning.
      expect(dish.mainIngredients.map((i) => i.name), ['Chicken breast']);
      expect(dish.seasonings.map((i) => i.name), ['Olive oil']);
    });

    test('tolerates decimal fields encoded as JSON strings', () {
      final json = _recipeJson(servings: '3.00')
        ..['nutrition'] = {
          'calories': '330.000',
          'protein_g': '62.000',
          'fat_g': '7.200',
          'carbs_g': '0.000',
        }
        ..['ingredients'] = [
          {
            'name': 'Chicken breast',
            'required_quantity': '450.000',
            'unit': 'GRAM',
            'is_optional': false,
          },
        ];

      final dish = RecipeDto.fromJson(json).toEntity();
      expect(dish.servings, 3);
      expect(dish.nutritionPerServing.energyKcal, closeTo(110.0, 1e-9)); // 330/3
      expect(dish.ingredients.single.quantity, 450.0);
    });

    test('falls back to an empty recipe when detail fields are missing', () {
      final dish = RecipeDto.fromJson({
        'id': 'r2',
        'name': 'Bare recipe',
        'default_servings': 1.0,
        'estimated_cooking_minutes': 10,
      }).toEntity();

      expect(dish.servings, 1);
      expect(dish.steps, isEmpty);
      expect(dish.ingredients, isEmpty);
      expect(dish.nutritionPerServing.energyKcal, 0);
    });
  });

  group('DishRepositoryImpl.getById()', () {
    test('reads GET /recipes/{id} and maps to a Dish', () async {
      final api = _MockApiClient();
      when(() => api.get(ApiPaths.recipe('r1')))
          .thenAnswer((_) async => _recipeJson());
      final repo = DishRepositoryImpl(DishRemoteDataSource(api));

      final res = await repo.getById('r1');

      final dish = res.fold((f) => fail('expected Right, got $f'), (d) => d);
      expect(dish.name, 'Grilled chicken breast');
      verify(() => api.get(ApiPaths.recipe('r1'))).called(1);
    });

    test('returns a Failure when the request throws', () async {
      final api = _MockApiClient();
      when(() => api.get(ApiPaths.recipe('nope'))).thenThrow(Exception('boom'));
      final repo = DishRepositoryImpl(DishRemoteDataSource(api));

      final res = await repo.getById('nope');

      expect(res.isLeft(), isTrue);
    });
  });
}
