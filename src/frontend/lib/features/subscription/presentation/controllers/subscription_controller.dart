import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/subscription/data/repositories/subscription_repository_impl.dart';
import 'package:sweepfood/features/subscription/domain/entities/subscription.dart';

part 'subscription_controller.g.dart';

/// P-02. Loads the current plan; falls back to the free default if the call
/// fails (the MVP is free either way).
@Riverpod(keepAlive: true)
class SubscriptionController extends _$SubscriptionController {
  @override
  Future<Subscription> build() async {
    final res = await ref.watch(subscriptionRepositoryProvider).current();
    return res.fold((_) => Subscription.freeDefault, (s) => s);
  }
}
