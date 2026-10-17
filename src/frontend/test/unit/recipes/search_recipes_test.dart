import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/features/dishes/data/datasources/dish_remote_data_source.dart';
import 'package:sweepfood/features/dishes/data/repositories/dish_repository_impl.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient mockApi;
  late DishRemoteDataSource dataSource;
  late DishRepositoryImpl repo;

  setUp(() {
    mockApi = _MockApiClient();
    dataSource = DishRemoteDataSource(mockApi);
    repo = DishRepositoryImpl(dataSource);
  });

  group('DishRepository searchRecipes', () {
    test('searchRecipes returns parsed recipes from API', () async {
      when(() => mockApi.get(
            '/recipes',
            query: {'q': 'canh chua', 'page': 1, 'per_page': 20},
          )).thenAnswer((_) async => {
            'items': [
              {
                'id': 'r1',
                'name': 'Canh chua cá lóc',
                'servings': 4,
                'prep_time_minutes': 15,
                'cook_time_minutes': 25,
                'difficulty': 'MEDIUM',
                'ingredients': [],
                'steps': [],
              }
            ],
            'total': 1,
            'page': 1,
            'per_page': 20,
          });

      final result = await repo.searchRecipes(query: 'canh chua');
      expect(result.isRight(), isTrue);
      final recipes = result.fold((l) => throw l, (r) => r);
      expect(recipes.length, 1);
      expect(recipes.first.id, 'r1');
      expect(recipes.first.name, 'Canh chua cá lóc');
      expect(recipes.first.servings, 4);
    });
  });
}
