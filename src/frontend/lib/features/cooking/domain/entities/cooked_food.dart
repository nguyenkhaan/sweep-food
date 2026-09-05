/// Leftover portions saved back into the pantry after cooking (D-06). Body
/// for `POST /cooking/sessions/{sessionId}/leftovers` — the backend derives
/// the batch's name/recipe context from the session, so only quantity/storage
/// info is sent.
class CookedFood {
  const CookedFood({
    required this.sessionId,
    required this.dishName,
    required this.servings,
    this.reminderInDays = 2,
  });

  final String sessionId;

  /// Local-only, for UI/snackbar text — not sent to the backend.
  final String dishName;

  /// Treated as a count of "portions" (`unit: PIECE`) — the backend has no
  /// serving-size concept, only quantity + unit.
  final int servings;

  /// "Nhắc dùng sau N ngày" — cooked food keeps 1–2 days.
  final int reminderInDays;

  DateTime get reminderAt =>
      DateTime.now().add(Duration(days: reminderInDays));

  Map<String, dynamic> toBody() => {
        'quantity': servings,
        'unit': 'PIECE',
        'storage_mode': 'REFRIGERATED',
        'expires_at': reminderAt.toUtc().toIso8601String(),
      };
}
