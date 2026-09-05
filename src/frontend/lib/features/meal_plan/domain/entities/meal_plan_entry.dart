import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'meal_plan_entry.freezed.dart';

/// The planned meals per day (M-01 grid columns). Backend enum has 4 values
/// (`BREAKFAST|LUNCH|DINNER|SNACK`).
enum MealSlot {
  breakfast('BREAKFAST'),
  lunch('LUNCH'),
  dinner('DINNER'),
  snack('SNACK');

  const MealSlot(this.wire);
  final String wire;

  String label(AppL10n l10n) => switch (this) {
    MealSlot.breakfast => l10n.mealSlotBreakfast,
    MealSlot.lunch => l10n.mealSlotLunch,
    MealSlot.dinner => l10n.mealSlotDinner,
    MealSlot.snack => l10n.mealSlotSnack,
  };

  static MealSlot fromWire(String? v) => MealSlot.values.firstWhere(
    (s) => s.wire == v,
    orElse: () => MealSlot.lunch,
  );
}

/// Backend `MealPlanItemStatus`. The M-01 grid doesn't surface this yet
/// (every entry the user creates shows as filled regardless) — carried
/// through so a later cooking-flow pass (Group D) can rely on it.
enum MealPlanItemStatus {
  planned('PLANNED'),
  completed('COMPLETED'),
  skipped('SKIPPED');

  const MealPlanItemStatus(this.wire);
  final String wire;

  static MealPlanItemStatus fromWire(String? v) =>
      MealPlanItemStatus.values.firstWhere(
        (s) => s.wire == v,
        orElse: () => MealPlanItemStatus.planned,
      );
}

/// One filled cell of the weekly grid — a `meal-plans/{id}/items/{item_id}`
/// row. [id] is the backend item id (needed for PATCH/DELETE, and later for
/// `/cooking/*`'s `meal_plan_item_id`).
@freezed
abstract class MealPlanEntry with _$MealPlanEntry {
  const MealPlanEntry._();

  const factory MealPlanEntry({
    required String id,
    required DateTime date,
    required MealSlot slot,
    required String dishId,
    required double servings,
    @Default(MealPlanItemStatus.planned) MealPlanItemStatus status,
    String? dishName,

    /// Known only for the lifetime of the session the dish was assigned in —
    /// the backend item has no image field, so this is lost on reload
    /// (nothing currently renders it; see IMPLEMENTATION_PLAN.md).
    String? dishImageUrl,
  }) = _MealPlanEntry;

  bool isAt(DateTime day, MealSlot s) =>
      slot == s &&
      date.year == day.year &&
      date.month == day.month &&
      date.day == day.day;
}
