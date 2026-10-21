import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/subscription/data/models/subscription_dto.dart';

class SubscriptionRemoteDataSource {
  SubscriptionRemoteDataSource(this._api);

  final ApiClient _api;

  Future<SubscriptionDto> current() async {
    final json = await _api.get(ApiPaths.subscription);
    return SubscriptionDto.fromJson(json as Map<String, dynamic>);
  }

  Future<void> registerPremiumInterest() => _api.post(ApiPaths.premiumInterest);
}
