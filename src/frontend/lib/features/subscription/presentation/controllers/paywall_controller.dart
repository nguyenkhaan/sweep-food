import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/analytics/analytics_events.dart';
import 'package:sweepfood/core/analytics/analytics_provider.dart';
import 'package:sweepfood/features/subscription/data/repositories/subscription_repository_impl.dart';
import 'package:sweepfood/features/subscription/presentation/controllers/subscription_controller.dart';

part 'paywall_controller.g.dart';

/// G-05 Paywall — interest capture ("Nhận thông báo khi ra mắt"). Nothing is
/// charged; a successful submit just flips [PaywallState.submitted].
class PaywallState {
  const PaywallState({
    this.submitting = false,
    this.submitted = false,
    this.error,
  });

  final bool submitting;
  final bool submitted;
  final String? error;

  PaywallState copyWith({bool? submitting, bool? submitted, String? error}) {
    return PaywallState(
      submitting: submitting ?? this.submitting,
      submitted: submitted ?? this.submitted,
      error: error,
    );
  }
}

@riverpod
class PaywallController extends _$PaywallController {
  @override
  PaywallState build() {
    ref.read(analyticsProvider).log(AnalyticsEvents.paywallViewed);
    return const PaywallState();
  }

  Future<void> submitInterest() async {
    if (state.submitting || state.submitted) return;
    state = state.copyWith(submitting: true, error: null);
    final res = await ref
        .read(subscriptionRepositoryProvider)
        .registerPremiumInterest();
    state = res.fold(
      (f) => state.copyWith(submitting: false, error: f.message),
      (_) {
        ref
            .read(analyticsProvider)
            .log(AnalyticsEvents.premiumInterestSubmitted);
        ref.invalidate(subscriptionControllerProvider);
        return state.copyWith(submitting: false, submitted: true);
      },
    );
  }
}
