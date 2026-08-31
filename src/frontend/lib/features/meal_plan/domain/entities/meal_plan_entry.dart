import 'package:freezed_annotation/freezed_annotation.dart';

part 'meal_plan_entry.freezed.dart';

/// The three planned meals per day (M-01 grid columns).
enum MealSlot {
  breakfast('breakfast', 'Sáng'),
  lunch('lunch', 'Trưa'),
  dinner('dinner', 'Tối');

  const MealSlot(this.wire, this.label);
  final String wire;
  final String label;

  static MealSlot fromWire(String? v) =>
      MealSlot.values.firstWhere((s) => s.wire == v, orElse: () => MealSlot.lunch);
}

/// One filled cell of the weekly grid.
@freezed
abstract class MealPlanEntry with _$MealPlanEntry {
  const MealPlanEntry._();

  const factory MealPlanEntry({
    required DateTime date,
    required MealSlot slot,
    required String dishId,
    String? dishName,
    String? dishImageUrl,
  }) = _MealPlanEntry;

  bool isAt(DateTime day, MealSlot s) =>
      slot == s &&
      date.year == day.year &&
      date.month == day.month &&
      date.day == day.day;
}
