/// The user's meal-ranking preference (spec 6.3.4, N-01). Feeds the `P` term
/// of the suggestion score. Chosen at onboarding, editable in Cài đặt → Tùy chọn.
enum DietaryPreference {
  balanced('balanced', 'Cân bằng', 'Đủ nhóm chất, không thiên lệch'),
  highProtein('high_protein', 'Nhiều protein', 'Ưu tiên thịt, cá, trứng, đậu'),
  lowCalorie('low_calorie', 'Ít năng lượng', 'Ưu tiên món dưới 400 kcal / khẩu phần'),
  moreVeg('more_veg', 'Nhiều rau', 'Ưu tiên món giàu rau củ, chất xơ');

  const DietaryPreference(this.wire, this.label, this.description);
  final String wire;
  final String label;
  final String description;

  static DietaryPreference fromWire(String? value) =>
      DietaryPreference.values.firstWhere(
        (p) => p.wire == value,
        orElse: () => DietaryPreference.balanced,
      );
}
