import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/subscription/domain/entities/subscription.dart';

part 'subscription_dto.freezed.dart';
part 'subscription_dto.g.dart';

@freezed
abstract class SubscriptionDto with _$SubscriptionDto {
  const SubscriptionDto._();

  const factory SubscriptionDto({
    required String tier,
    @Default(<String>[]) List<String> perks,
    @JsonKey(name: 'premium_interest_registered')
    @Default(false)
    bool premiumInterestRegistered,
  }) = _SubscriptionDto;

  factory SubscriptionDto.fromJson(Map<String, dynamic> json) =>
      _$SubscriptionDtoFromJson(json);

  Subscription toEntity() => Subscription(
        tier: SubscriptionTier.fromWire(tier),
        perks: perks,
        premiumInterestRegistered: premiumInterestRegistered,
      );
}
