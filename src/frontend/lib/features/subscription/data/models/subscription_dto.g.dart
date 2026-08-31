// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'subscription_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_SubscriptionDto _$SubscriptionDtoFromJson(Map<String, dynamic> json) =>
    _SubscriptionDto(
      tier: json['tier'] as String,
      perks:
          (json['perks'] as List<dynamic>?)?.map((e) => e as String).toList() ??
          const <String>[],
      premiumInterestRegistered:
          json['premium_interest_registered'] as bool? ?? false,
    );

Map<String, dynamic> _$SubscriptionDtoToJson(_SubscriptionDto instance) =>
    <String, dynamic>{
      'tier': instance.tier,
      'perks': instance.perks,
      'premium_interest_registered': instance.premiumInterestRegistered,
    };
