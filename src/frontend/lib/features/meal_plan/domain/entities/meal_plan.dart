import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/features/meal_plan/domain/entities/meal_plan_entry.dart';

part 'meal_plan.freezed.dart';

/// M-01 weekly menu. `weekStart` is always a Monday (date-only).
@freezed
abstract class MealPlan with _$MealPlan {
  const MealPlan._();

  const factory MealPlan({
    required DateTime weekStart,
    @Default(<MealPlanEntry>[]) List<MealPlanEntry> entries,
  }) = _MealPlan;

  /// The Monday of the week containing [d].
  static DateTime weekStartOf(DateTime d) {
    final dateOnly = DateTime(d.year, d.month, d.day);
    return dateOnly.subtract(Duration(days: dateOnly.weekday - 1));
  }

  List<DateTime> get days =>
      [for (var i = 0; i < 7; i++) weekStart.add(Duration(days: i))];

  MealPlanEntry? entryAt(DateTime day, MealSlot slot) {
    for (final e in entries) {
      if (e.isAt(day, slot)) return e;
    }
    return null;
  }

  int get filledCount => entries.length;

  /// Add / replace the entry in a cell.
  MealPlan withEntry(MealPlanEntry entry) => copyWith(
        entries: [
          for (final e in entries)
            if (!e.isAt(entry.date, entry.slot)) e,
          entry,
        ],
      );

  MealPlan withoutEntry(DateTime day, MealSlot slot) => copyWith(
        entries: [for (final e in entries) if (!e.isAt(day, slot)) e],
      );
}
