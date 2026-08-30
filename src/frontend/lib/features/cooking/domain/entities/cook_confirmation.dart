/// How much stock to deduct when a dish is marked cooked (D-03).
enum CookMode {
  exact('exact', 'Dùng đúng định lượng', 'Trừ kho theo công thức'),
  half('half', 'Dùng một nửa', 'Trừ 50% lượng dự kiến'),
  all('all', 'Dùng hết những gì đang có', 'Đưa các nguyên liệu này về 0'),
  custom('custom', 'Tự điều chỉnh', 'Chỉnh từng nguyên liệu');

  const CookMode(this.wire, this.label, this.description);
  final String wire;
  final String label;
  final String description;
}

/// Body for `POST /dishes/{id}/cook`.
class CookConfirmation {
  const CookConfirmation({
    required this.dishId,
    required this.mode,
    required this.servingsCooked,
    this.customUsage = const {},
  });

  final String dishId;
  final CookMode mode;
  final int servingsCooked;

  /// Only for [CookMode.custom]: ingredient name → actual quantity used.
  final Map<String, double> customUsage;

  Map<String, dynamic> toBody() => {
        'mode': mode.wire,
        'servings_cooked': servingsCooked,
        if (mode == CookMode.custom) 'custom_usage': customUsage,
      };
}
