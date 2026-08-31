import 'package:freezed_annotation/freezed_annotation.dart';

part 'subscription.freezed.dart';

/// Spec 12.1. In the MVP everyone is [SubscriptionTier.free] and every feature
/// is unlocked (see `core/entitlements/`); this entity backs the P-02 screen.
enum SubscriptionTier {
  free('free', 'Bản đầy đủ · miễn phí'),
  premiumMonthly('premium_monthly', 'Premium tháng'),
  premiumYearly('premium_yearly', 'Premium năm'),
  premiumFamily('premium_family', 'Premium gia đình');

  const SubscriptionTier(this.wire, this.label);
  final String wire;
  final String label;

  static SubscriptionTier fromWire(String? v) => SubscriptionTier.values
      .firstWhere((t) => t.wire == v, orElse: () => SubscriptionTier.free);

  bool get isPremium => this != SubscriptionTier.free;
}

@freezed
abstract class Subscription with _$Subscription {
  const Subscription._();

  const factory Subscription({
    required SubscriptionTier tier,
    @Default(<String>[]) List<String> perks,

    /// Whether this device has already registered premium interest (G-05).
    @Default(false) bool premiumInterestRegistered,
  }) = _Subscription;

  static const freeDefault = Subscription(
    tier: SubscriptionTier.free,
    perks: [
      'Kho nguyên liệu không giới hạn',
      'Quét tem & hóa đơn không giới hạn',
      'Gợi ý món & dinh dưỡng đầy đủ',
      'Thực đơn tuần, danh sách mua sắm, báo cáo',
    ],
  );
}
