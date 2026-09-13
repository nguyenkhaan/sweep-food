import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/auth/domain/entities/active_session.dart';
import 'package:sweepfood/features/auth/domain/entities/user.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

part 'auth_dto.freezed.dart';
part 'auth_dto.g.dart';

/// `POST /auth/register`, `/register/resend-otp`, `/password/reset`,
/// `/password/change` — the backend returns the generated OTP (MVP/local) and
/// its lifetime. The frontend only needs the lifetime for the resend timer.
@freezed
abstract class OtpIssueDto with _$OtpIssueDto {
  const factory OtpIssueDto({
    required String otp,
    @JsonKey(name: 'expires_in_seconds') required int expiresInSeconds,
  }) = _OtpIssueDto;

  factory OtpIssueDto.fromJson(Map<String, dynamic> json) =>
      _$OtpIssueDtoFromJson(json);
}

/// `POST /auth/login` response — the token pair plus session metadata. There is
/// **no** `user` block; fetch `GET /users/profile` separately.
@freezed
abstract class TokenPairDto with _$TokenPairDto {
  const factory TokenPairDto({
    @JsonKey(name: 'access_token') required String accessToken,
    @JsonKey(name: 'refresh_token') required String refreshToken,
    @JsonKey(name: 'token_type') String? tokenType,
    @JsonKey(name: 'access_expires_in_seconds') int? accessExpiresInSeconds,
    @JsonKey(name: 'refresh_expires_in_seconds') int? refreshExpiresInSeconds,
    @JsonKey(name: 'session_id') String? sessionId,
  }) = _TokenPairDto;

  factory TokenPairDto.fromJson(Map<String, dynamic> json) =>
      _$TokenPairDtoFromJson(json);
}

/// `POST /auth/token/refresh` response — a fresh access token only (the backend
/// does not rotate the refresh token).
@freezed
abstract class AccessTokenDto with _$AccessTokenDto {
  const factory AccessTokenDto({
    @JsonKey(name: 'access_token') required String accessToken,
    @JsonKey(name: 'token_type') String? tokenType,
    @JsonKey(name: 'access_expires_in_seconds') int? accessExpiresInSeconds,
  }) = _AccessTokenDto;

  factory AccessTokenDto.fromJson(Map<String, dynamic> json) =>
      _$AccessTokenDtoFromJson(json);
}

/// One row of `GET /auth/sessions` — a non-revoked, non-expired login session
/// owned by the caller. Timestamps arrive as ISO-8601 strings.
@freezed
abstract class AuthSessionDto with _$AuthSessionDto {
  const AuthSessionDto._();

  const factory AuthSessionDto({
    required String id,
    @JsonKey(name: 'ip_address') String? ipAddress,
    @JsonKey(name: 'user_agent') String? userAgent,
    @JsonKey(name: 'expires_at') required DateTime expiresAt,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'last_used_at') DateTime? lastUsedAt,
  }) = _AuthSessionDto;

  factory AuthSessionDto.fromJson(Map<String, dynamic> json) =>
      _$AuthSessionDtoFromJson(json);

  ActiveSession toEntity() => ActiveSession(
        id: id,
        ipAddress: ipAddress,
        userAgent: userAgent,
        expiresAt: expiresAt,
        createdAt: createdAt,
        lastUsedAt: lastUsedAt,
      );
}

/// `GET /users/profile` payload. `name`/`email` are nullable; the meal-ranking
/// preference and avatar live in the free-form `preferences` map.
@freezed
abstract class UserProfileDto with _$UserProfileDto {
  const UserProfileDto._();

  const factory UserProfileDto({
    @JsonKey(name: 'user_id') required String userId,
    String? name,
    required String phone,
    @JsonKey(name: 'phone_verified_at') String? phoneVerifiedAt,
    String? email,
    @JsonKey(name: 'email_verified_at') String? emailVerifiedAt,
    @Default(<String, dynamic>{}) Map<String, dynamic> preferences,
  }) = _UserProfileDto;

  factory UserProfileDto.fromJson(Map<String, dynamic> json) =>
      _$UserProfileDtoFromJson(json);

  User toEntity() {
    final rawDiet = preferences['dietary_preference'];
    final rawAvatar = preferences['avatar_url'];
    return User(
      id: userId,
      phone: phone,
      name: name,
      email: email,
      dietaryPreference:
          rawDiet is String ? DietaryPreference.fromWire(rawDiet) : null,
      avatarUrl: rawAvatar is String ? rawAvatar : null,
    );
  }
}
