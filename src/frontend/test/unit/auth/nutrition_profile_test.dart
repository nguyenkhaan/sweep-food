import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/features/auth/data/models/auth_dto.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';
import 'package:sweepfood/shared/domain/nutrition_profile.dart';

void main() {
  group('NutritionProfile', () {
    test('parses full preferences map and serializes back cleanly', () {
      final profile = NutritionProfile.fromPreferencesMap({
        'household_size': 3,
        'diet': 'vegetarian',
        'health_conditions': [
          'nguoi_cao_huyet_ap',
          'nguoi_tieu_duong',
          'nguoi_cao_huyet_ap',
          'invalid_code',
        ],
        'allergies': ['shellfish', 'peanut', 'shellfish'],
        'disliked_ingredients': [' rau mùi ', '', 'Rau Mùi', 'Hành tây'],
      });

      expect(profile.householdSize, 3);
      expect(profile.diet, DietaryPreference.vegetarian);
      expect(profile.healthConditions, [
        HealthCondition.hypertension,
        HealthCondition.diabetes,
      ]);
      expect(profile.allergies, [AllergyGroup.shellfish, AllergyGroup.peanut]);
      expect(profile.dislikedIngredients, ['rau mùi', 'Hành tây']);
      expect(profile.hasStrictFilters, isTrue);
      expect(profile.activeConstraintCount, 7);

      expect(profile.toPreferencesMap(), {
        'household_size': 3,
        'diet': 'vegetarian',
        'health_conditions': ['nguoi_cao_huyet_ap', 'nguoi_tieu_duong'],
        'allergies': ['shellfish', 'peanut'],
        'disliked_ingredients': ['rau mùi', 'Hành tây'],
      });
    });

    test(
      'falls back to legacy dietary_preference and clamps household_size',
      () {
        final profile = NutritionProfile.fromPreferencesMap({
          'household_size': 99,
          'dietary_preference': 'HIGH_PROTEIN',
        });

        expect(profile.householdSize, NutritionProfile.maxHouseholdSize);
        expect(profile.diet, DietaryPreference.highProtein);
        expect(profile.hasStrictFilters, isFalse);
      },
    );

    test('UserProfileDto maps preferences into User.nutritionProfile', () {
      final dto = UserProfileDto.fromJson({
        'user_id': 'u-1',
        'phone': '+84901234567',
        'name': 'Minh',
        'preferences': {
          'household_size': 2,
          'diet': 'more_veg',
          'allergies': ['dairy'],
        },
      });

      final user = dto.toEntity();
      expect(user.dietaryPreference, DietaryPreference.moreVeg);
      expect(user.nutritionProfile.householdSize, 2);
      expect(user.nutritionProfile.diet, DietaryPreference.moreVeg);
      expect(user.nutritionProfile.allergies, [AllergyGroup.dairy]);
    });
  });
}
