// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_OtpIssueDto _$OtpIssueDtoFromJson(Map<String, dynamic> json) => _OtpIssueDto(
  otp: json['otp'] as String,
  expiresInSeconds: (json['expires_in_seconds'] as num).toInt(),
);

Map<String, dynamic> _$OtpIssueDtoToJson(_OtpIssueDto instance) =>
    <String, dynamic>{
      'otp': instance.otp,
      'expires_in_seconds': instance.expiresInSeconds,
    };

_TokenPairDto _$TokenPairDtoFromJson(Map<String, dynamic> json) =>
    _TokenPairDto(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      tokenType: json['token_type'] as String?,
      accessExpiresInSeconds: (json['access_expires_in_seconds'] as num?)
          ?.toInt(),
      refreshExpiresInSeconds: (json['refresh_expires_in_seconds'] as num?)
          ?.toInt(),
      sessionId: json['session_id'] as String?,
    );

Map<String, dynamic> _$TokenPairDtoToJson(_TokenPairDto instance) =>
    <String, dynamic>{
      'access_token': instance.accessToken,
      'refresh_token': instance.refreshToken,
      'token_type': instance.tokenType,
      'access_expires_in_seconds': instance.accessExpiresInSeconds,
      'refresh_expires_in_seconds': instance.refreshExpiresInSeconds,
      'session_id': instance.sessionId,
    };

_AccessTokenDto _$AccessTokenDtoFromJson(Map<String, dynamic> json) =>
    _AccessTokenDto(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String?,
      accessExpiresInSeconds: (json['access_expires_in_seconds'] as num?)
          ?.toInt(),
    );

Map<String, dynamic> _$AccessTokenDtoToJson(_AccessTokenDto instance) =>
    <String, dynamic>{
      'access_token': instance.accessToken,
      'token_type': instance.tokenType,
      'access_expires_in_seconds': instance.accessExpiresInSeconds,
    };

_AuthSessionDto _$AuthSessionDtoFromJson(Map<String, dynamic> json) =>
    _AuthSessionDto(
      id: json['id'] as String,
      ipAddress: json['ip_address'] as String?,
      userAgent: json['user_agent'] as String?,
      expiresAt: DateTime.parse(json['expires_at'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
      lastUsedAt: json['last_used_at'] == null
          ? null
          : DateTime.parse(json['last_used_at'] as String),
    );

Map<String, dynamic> _$AuthSessionDtoToJson(_AuthSessionDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'ip_address': instance.ipAddress,
      'user_agent': instance.userAgent,
      'expires_at': instance.expiresAt.toIso8601String(),
      'created_at': instance.createdAt.toIso8601String(),
      'last_used_at': instance.lastUsedAt?.toIso8601String(),
    };

_UserProfileDto _$UserProfileDtoFromJson(Map<String, dynamic> json) =>
    _UserProfileDto(
      userId: json['user_id'] as String,
      name: json['name'] as String?,
      phone: json['phone'] as String,
      phoneVerifiedAt: json['phone_verified_at'] as String?,
      email: json['email'] as String?,
      emailVerifiedAt: json['email_verified_at'] as String?,
      preferences:
          json['preferences'] as Map<String, dynamic>? ??
          const <String, dynamic>{},
    );

Map<String, dynamic> _$UserProfileDtoToJson(_UserProfileDto instance) =>
    <String, dynamic>{
      'user_id': instance.userId,
      'name': instance.name,
      'phone': instance.phone,
      'phone_verified_at': instance.phoneVerifiedAt,
      'email': instance.email,
      'email_verified_at': instance.emailVerifiedAt,
      'preferences': instance.preferences,
    };
