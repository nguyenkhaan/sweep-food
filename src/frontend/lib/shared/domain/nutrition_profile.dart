import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

part 'nutrition_profile.freezed.dart';

/// Health conditions mapped 1-to-1 to hard scenario rules on the backend.
enum HealthCondition {
  diabetes('nguoi_tieu_duong'),
  hypertension('nguoi_cao_huyet_ap'),
  gout('nguoi_benh_gout'),
  gastritis('nguoi_dau_da_day'),
  ketoLowCarb('an_kieng_keto_lowcarb');

  const HealthCondition(this.wire);
  final String wire;

  String label(AppL10n l10n) => switch (this) {
    HealthCondition.diabetes => l10n.healthCondDiabetes,
    HealthCondition.hypertension => l10n.healthCondHypertension,
    HealthCondition.gout => l10n.healthCondGout,
    HealthCondition.gastritis => l10n.healthCondGastritis,
    HealthCondition.ketoLowCarb => l10n.healthCondKetoLowCarb,
  };

  String description(AppL10n l10n) => switch (this) {
    HealthCondition.diabetes => l10n.healthCondDiabetesDesc,
    HealthCondition.hypertension => l10n.healthCondHypertensionDesc,
    HealthCondition.gout => l10n.healthCondGoutDesc,
    HealthCondition.gastritis => l10n.healthCondGastritisDesc,
    HealthCondition.ketoLowCarb => l10n.healthCondKetoLowCarbDesc,
  };

  static HealthCondition? fromWire(String? value) {
    final normalized = value?.trim().toLowerCase();
    for (final item in HealthCondition.values) {
      if (item.wire == normalized) return item;
    }
    return null;
  }
}

/// Allergen groups mapped to strict backend / AI exclusion rules.
enum AllergyGroup {
  shellfish('shellfish'),
  fish('fish'),
  peanut('peanut'),
  egg('egg'),
  dairy('dairy'),
  soy('soy'),
  gluten('gluten'),
  sesame('sesame');

  const AllergyGroup(this.wire);
  final String wire;

  String label(AppL10n l10n) => switch (this) {
    AllergyGroup.shellfish => l10n.allergyShellfish,
    AllergyGroup.fish => l10n.allergyFish,
    AllergyGroup.peanut => l10n.allergyPeanut,
    AllergyGroup.egg => l10n.allergyEgg,
    AllergyGroup.dairy => l10n.allergyDairy,
    AllergyGroup.soy => l10n.allergySoy,
    AllergyGroup.gluten => l10n.allergyGluten,
    AllergyGroup.sesame => l10n.allergySesame,
  };

  String examples(AppL10n l10n) => switch (this) {
    AllergyGroup.shellfish => l10n.allergyShellfishExamples,
    AllergyGroup.fish => l10n.allergyFishExamples,
    AllergyGroup.peanut => l10n.allergyPeanutExamples,
    AllergyGroup.egg => l10n.allergyEggExamples,
    AllergyGroup.dairy => l10n.allergyDairyExamples,
    AllergyGroup.soy => l10n.allergySoyExamples,
    AllergyGroup.gluten => l10n.allergyGlutenExamples,
    AllergyGroup.sesame => l10n.allergySesameExamples,
  };

  static AllergyGroup? fromWire(String? value) {
    final normalized = value?.trim().toLowerCase();
    for (final item in AllergyGroup.values) {
      if (item.wire == normalized) return item;
    }
    return null;
  }
}

/// Persisted nutrition & dietary profile stored inside `users.preferences`.
@freezed
abstract class NutritionProfile with _$NutritionProfile {
  const NutritionProfile._();

  static const int defaultHouseholdSize = 4;
  static const int minHouseholdSize = 1;
  static const int maxHouseholdSize = 10;
  static const int maxDislikedIngredients = 50;

  const factory NutritionProfile({
    @Default(NutritionProfile.defaultHouseholdSize) int householdSize,
    @Default(DietaryPreference.balanced) DietaryPreference diet,
    @Default(<HealthCondition>[]) List<HealthCondition> healthConditions,
    @Default(<AllergyGroup>[]) List<AllergyGroup> allergies,
    @Default(<String>[]) List<String> dislikedIngredients,
  }) = _NutritionProfile;

  /// Parses the 5 nutrition keys from a `users.preferences` JSON map.
  factory NutritionProfile.fromPreferencesMap(Map<String, dynamic> map) {
    final rawSize = map['household_size'];
    final parsedSize = rawSize is int
        ? rawSize
        : (rawSize is num ? rawSize.toInt() : defaultHouseholdSize);
    final householdSize = parsedSize.clamp(minHouseholdSize, maxHouseholdSize);

    final rawDiet = map['diet'] ?? map['dietary_preference'];
    final diet = rawDiet is String
        ? DietaryPreference.fromWire(rawDiet)
        : DietaryPreference.balanced;

    final healthConditions = <HealthCondition>[];
    final rawHealth = map['health_conditions'];
    if (rawHealth is List) {
      for (final item in rawHealth) {
        final parsed = HealthCondition.fromWire(item?.toString());
        if (parsed != null && !healthConditions.contains(parsed)) {
          healthConditions.add(parsed);
        }
      }
    }

    final allergies = <AllergyGroup>[];
    final rawAllergies = map['allergies'];
    if (rawAllergies is List) {
      for (final item in rawAllergies) {
        final parsed = AllergyGroup.fromWire(item?.toString());
        if (parsed != null && !allergies.contains(parsed)) {
          allergies.add(parsed);
        }
      }
    }

    final disliked = <String>[];
    final seenLower = <String>{};
    final rawDisliked = map['disliked_ingredients'];
    if (rawDisliked is List) {
      for (final item in rawDisliked) {
        final cleaned = item?.toString().trim() ?? '';
        if (cleaned.isEmpty) continue;
        final lower = cleaned.toLowerCase();
        if (seenLower.add(lower)) {
          disliked.add(cleaned);
        }
        if (disliked.length >= maxDislikedIngredients) break;
      }
    }

    return NutritionProfile(
      householdSize: householdSize,
      diet: diet,
      healthConditions: healthConditions,
      allergies: allergies,
      dislikedIngredients: disliked,
    );
  }

  /// Serializes only the 5 nutrition keys for shallow-merge `PATCH /users/profile`.
  Map<String, dynamic> toPreferencesMap() => {
    'household_size': householdSize.clamp(minHouseholdSize, maxHouseholdSize),
    'diet': diet.wire,
    'health_conditions': healthConditions.map((e) => e.wire).toList(),
    'allergies': allergies.map((e) => e.wire).toList(),
    'disliked_ingredients': dislikedIngredients,
  };

  bool get hasStrictFilters =>
      diet.isHardFilter ||
      healthConditions.isNotEmpty ||
      allergies.isNotEmpty ||
      dislikedIngredients.isNotEmpty;

  int get activeConstraintCount =>
      (diet.isHardFilter ? 1 : 0) +
      healthConditions.length +
      allergies.length +
      dislikedIngredients.length;
}
