/// Storage advice shown in the near-expiry detail sheet (T-02). Static,
/// category-keyed copy — sourced from FoodKeeper-style guidance (see P-06).
abstract final class ExpiryTips {
  static const _byKeyword = <String, String>{
    'rau': 'Rau ăn lá nên dùng trong ngày để giữ độ tươi và dinh dưỡng. '
        'Kiểm tra lá có bị úa hoặc nhũn không trước khi nấu.',
    'trái': 'Trái cây chín nhanh ở nhiệt độ phòng. Cho vào ngăn mát để giữ '
        'thêm 2–3 ngày; dùng ngay khi vỏ bắt đầu nhăn.',
    'thịt': 'Thịt tươi để ngăn mát nên nấu trong 1–2 ngày. Nếu chưa dùng kịp, '
        'cấp đông ngay để giữ chất lượng.',
    'cá': 'Cá và hải sản rất nhanh hỏng — nấu trong ngày hoặc cấp đông. '
        'Ngửi thấy mùi tanh gắt thì nên bỏ.',
    'sữa': 'Sữa và chế phẩm từ sữa giữ trong ngăn mát dưới 4°C. Dùng trước hạn '
        'và kiểm tra mùi trước khi uống.',
    'trứng': 'Trứng để ngăn mát dùng tốt trong vài tuần. Thử thả vào nước: '
        'trứng nổi là đã cũ.',
  };

  /// A tip for [category]; falls back to a generic reminder.
  static String forCategory(String category) {
    final c = category.toLowerCase();
    for (final e in _byKeyword.entries) {
      if (c.contains(e.key)) return e.value;
    }
    return 'Ưu tiên dùng nguyên liệu này sớm. Luôn kiểm tra màu sắc, mùi và '
        'trạng thái thực phẩm trước khi chế biến.';
  }
}
