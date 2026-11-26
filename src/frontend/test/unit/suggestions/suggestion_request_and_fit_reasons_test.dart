import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/features/suggestions/data/models/recommendation_dto.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

void main() {
  group('SuggestionRequest.toBody', () {
    test(
      'never maps moreVeg to vegetarian and delegates profile to backend',
      () {
        const request = SuggestionRequest(
          pantryItems: [
            RecommendationPantryItemDraft(
              name: 'Cải thìa',
              code: '4001',
              quantityG: 250,
              hoursToExpire: 24,
            ),
          ],
          dietaryPreference: DietaryPreference.moreVeg,
          mealType: MealType.dinner,
          householdSize: 2,
        );

        final body = request.toBody();

        expect(body.keys, equals(['items']));
        expect(body['dietary_restrictions'], isNull);
        expect(body['scenario_type'], isNull);
        expect(body['allergies'], isNull);
        expect(body['disliked_ingredients'], isNull);
        expect((body['items'] as List).length, 1);
      },
    );
  });

  group('RecommendationItemDto fit_reasons parsing', () {
    test('extracts trimmed non-empty fit_reasons from recommendation JSON', () {
      final dto = RecommendationItemDto.fromJson({
        'recipe_id': 'r-1',
        'recipe_name': 'Đậu phụ sốt cà chua',
        'rank': 1,
        'rank_score': 2.5,
        'fit_reasons': [
          ' Ít muối, hợp người cao huyết áp ',
          '',
          '≈ 320 kcal/suất · 18 g đạm',
          'Không có hải sản có vỏ',
        ],
      });

      expect(dto.fitReasons, [
        'Ít muối, hợp người cao huyết áp',
        '≈ 320 kcal/suất · 18 g đạm',
        'Không có hải sản có vỏ',
      ]);
    });

    test('defaults fitReasons to empty list when omitted', () {
      final dto = RecommendationItemDto.fromJson({
        'recipe_id': 'r-2',
        'recipe_name': 'Canh rau cải',
        'rank': 2,
      });

      expect(dto.fitReasons, isEmpty);
    });
  });
}
