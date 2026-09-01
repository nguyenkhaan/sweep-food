import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/subscription/data/datasources/subscription_remote_data_source.dart';
import 'package:sweepfood/features/subscription/domain/entities/subscription.dart';
import 'package:sweepfood/features/subscription/domain/repositories/subscription_repository.dart';

part 'subscription_repository_impl.g.dart';

@Riverpod(keepAlive: true)
SubscriptionRepository subscriptionRepository(Ref ref) =>
    SubscriptionRepositoryImpl(
      SubscriptionRemoteDataSource(ref.watch(apiClientProvider)),
    );

class SubscriptionRepositoryImpl implements SubscriptionRepository {
  SubscriptionRepositoryImpl(this._remote);

  final SubscriptionRemoteDataSource _remote;

  @override
  Future<Result<Subscription>> current() =>
      runGuarded(() async => (await _remote.current()).toEntity());

  @override
  Future<Result<void>> registerPremiumInterest({
    String? planId,
    String? email,
  }) =>
      guardVoid(
        () => _remote.registerPremiumInterest(planId: planId, email: email),
      );
}
