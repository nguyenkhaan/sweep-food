// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_UserDto _$UserDtoFromJson(Map<String, dynamic> json) => _UserDto(
  id: json['id'] as String,
  name: json['name'] as String,
  email: json['email'] as String,
  dietaryPreference: json['dietary_preference'] as String?,
  avatarUrl: json['avatar_url'] as String?,
);

Map<String, dynamic> _$UserDtoToJson(_UserDto instance) => <String, dynamic>{
  'id': instance.id,
  'name': instance.name,
  'email': instance.email,
  'dietary_preference': instance.dietaryPreference,
  'avatar_url': instance.avatarUrl,
};

_SessionDto _$SessionDtoFromJson(Map<String, dynamic> json) => _SessionDto(
  user: UserDto.fromJson(json['user'] as Map<String, dynamic>),
  accessToken: json['access_token'] as String,
  refreshToken: json['refresh_token'] as String,
);

Map<String, dynamic> _$SessionDtoToJson(_SessionDto instance) =>
    <String, dynamic>{
      'user': instance.user,
      'access_token': instance.accessToken,
      'refresh_token': instance.refreshToken,
    };

_TokenPairDto _$TokenPairDtoFromJson(Map<String, dynamic> json) =>
    _TokenPairDto(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
    );

Map<String, dynamic> _$TokenPairDtoToJson(_TokenPairDto instance) =>
    <String, dynamic>{
      'access_token': instance.accessToken,
      'refresh_token': instance.refreshToken,
    };
