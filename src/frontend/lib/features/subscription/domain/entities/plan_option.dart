import 'package:flutter/foundation.dart';

/// A purchasable plan shown on the paywall (G-05). Prices are **"dự kiến"** —
/// the MVP only captures interest, nothing is charged.
@immutable
class PlanOption {
  const PlanOption({
    required this.id,
    required this.name,
    required this.priceLabel,
    required this.periodLabel,
    this.subtitle,
    this.savingLabel,
    this.comingSoon = false,
  });

  final String id;
  final String name;

  /// e.g. "39.000đ" or "Sắp có".
  final String priceLabel;

  /// e.g. "/ tháng (dự kiến)".
  final String periodLabel;
  final String? subtitle;
  final String? savingLabel;
  final bool comingSoon;

  static const monthly = PlanOption(
    id: 'premium_monthly',
    name: 'Premium tháng',
    priceLabel: '39.000đ',
    periodLabel: '/ tháng (dự kiến)',
    subtitle: 'Thanh toán hằng tháng',
  );

  static const yearly = PlanOption(
    id: 'premium_yearly',
    name: 'Premium năm',
    priceLabel: '299.000đ',
    periodLabel: '/ năm (dự kiến)',
    subtitle: '299.000đ / năm · ~24.900đ / tháng',
    savingLabel: 'Tiết kiệm 36%',
  );

  static const family = PlanOption(
    id: 'premium_family',
    name: 'Premium gia đình',
    priceLabel: 'Sắp có',
    periodLabel: '',
    subtitle: 'Chia sẻ cho 4 người',
    comingSoon: true,
  );

  static const all = [monthly, yearly, family];
}
