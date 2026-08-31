import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/subscription/domain/entities/subscription.dart';

abstract interface class SubscriptionRepository {
  /// `GET /subscription` — current tier + perks.
  Future<Result<Subscription>> current();

  /// `POST /subscription/premium-interest` — capture "báo tôi khi ra mắt"
  /// (G-05). MVP: nothing is charged.
  Future<Result<void>> registerPremiumInterest({String? planId, String? email});
}
