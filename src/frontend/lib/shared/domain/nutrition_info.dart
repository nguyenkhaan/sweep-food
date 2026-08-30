/// Estimated macros for a dish / serving / per-100g reference (spec 6.3.4).
class NutritionInfo {
  const NutritionInfo({
    required this.energyKcal,
    required this.proteinG,
    required this.carbG,
    required this.lipidG,
  });

  const NutritionInfo.zero()
      : energyKcal = 0,
        proteinG = 0,
        carbG = 0,
        lipidG = 0;

  final double energyKcal;
  final double proteinG;
  final double carbG;
  final double lipidG;

  NutritionInfo scale(double factor) => NutritionInfo(
        energyKcal: energyKcal * factor,
        proteinG: proteinG * factor,
        carbG: carbG * factor,
        lipidG: lipidG * factor,
      );

  NutritionInfo operator +(NutritionInfo other) => NutritionInfo(
        energyKcal: energyKcal + other.energyKcal,
        proteinG: proteinG + other.proteinG,
        carbG: carbG + other.carbG,
        lipidG: lipidG + other.lipidG,
      );

  /// Per-serving from a whole-dish total.
  NutritionInfo perServing(int servings) =>
      servings <= 0 ? this : scale(1 / servings);
}
