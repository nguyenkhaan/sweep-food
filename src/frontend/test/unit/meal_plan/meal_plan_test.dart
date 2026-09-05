import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';

void main() {
  test('weekStartOf() returns the Monday of the week', () {
    // 2026-08-31 is a Monday; 2026-09-03 is the Thursday of the same week.
    expect(MealPlan.weekStartOf(DateTime(2026, 8, 31)), DateTime(2026, 8, 31));
    expect(MealPlan.weekStartOf(DateTime(2026, 9, 3)), DateTime(2026, 8, 31));
    expect(MealPlan.weekStartOf(DateTime(2026, 9, 6)), DateTime(2026, 8, 31));
  });

  test('days spans the 7-day week', () {
    final plan = MealPlan(weekStart: DateTime(2026, 8, 31));
    expect(plan.days.first, DateTime(2026, 8, 31));
    expect(plan.days.last, DateTime(2026, 9, 6));
    expect(plan.days, hasLength(7));
  });

  test('withEntry replaces the cell, withoutEntry clears it', () {
    final monday = DateTime(2026, 8, 31);
    var plan = MealPlan(weekStart: monday);

    plan = plan.withEntry(
      MealPlanEntry(
        id: 'item-1',
        date: monday,
        slot: MealSlot.lunch,
        dishId: 'd1',
        servings: 2,
      ),
    );
    expect(plan.entryAt(monday, MealSlot.lunch)?.dishId, 'd1');

    // Same cell → replace, not append.
    plan = plan.withEntry(
      MealPlanEntry(
        id: 'item-1',
        date: monday,
        slot: MealSlot.lunch,
        dishId: 'd2',
        servings: 2,
      ),
    );
    expect(plan.filledCount, 1);
    expect(plan.entryAt(monday, MealSlot.lunch)?.dishId, 'd2');

    plan = plan.withoutEntry(monday, MealSlot.lunch);
    expect(plan.entryAt(monday, MealSlot.lunch), isNull);
    expect(plan.filledCount, 0);
  });
}
