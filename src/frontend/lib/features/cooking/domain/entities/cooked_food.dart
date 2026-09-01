/// Leftover portions saved back into the "Ăn liền" tier with a use-by reminder
/// (D-06). Body for `POST /pantry/cooked-food`.
class CookedFood {
  const CookedFood({
    required this.dishId,
    required this.dishName,
    required this.servings,
    this.reminderInDays = 2,
  });

  final String dishId;
  final String dishName;
  final int servings;

  /// "Nhắc dùng sau N ngày" — cooked food keeps 1–2 days.
  final int reminderInDays;

  DateTime get reminderAt =>
      DateTime.now().add(Duration(days: reminderInDays));

  Map<String, dynamic> toBody() => {
        'dish_id': dishId,
        'name': dishName,
        'servings': servings,
        'reminder_at': reminderAt.toIso8601String(),
      };
}
