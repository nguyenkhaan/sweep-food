import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/features/auth/domain/entities/session.dart';
import 'package:frontend/features/auth/domain/entities/user.dart';
import 'package:frontend/shared/domain/dietary_preference.dart';

part 'auth_dto.freezed.dart';
part 'auth_dto.g.dart';

/// `/auth/me` payload and the `user` block embedded in a login/register response.
@freezed
abstract class UserDto with _$UserDto {
  const UserDto._();

  const factory UserDto({
    required String id,
    required String name,
    required String email,
    @JsonKey(name: 'dietary_preference') String? dietaryPreference,
    @JsonKey(name: 'avatar_url') String? avatarUrl,
  }) = _UserDto;

  factory UserDto.fromJson(Map<String, dynamic> json) =>
      _$UserDtoFromJson(json);

  User toEntity() => User(
        id: id,
        name: name,
        email: email,
        dietaryPreference: dietaryPreference == null
            ? null
            : DietaryPreference.fromWire(dietaryPreference),
        avatarUrl: avatarUrl,
      );
}

/// The `POST /auth/login` and `POST /auth/register` response envelope.
@freezed
abstract class SessionDto with _$SessionDto {
  const SessionDto._();

  const factory SessionDto({
    required UserDto user,
    @JsonKey(name: 'access_token') required String accessToken,
    @JsonKey(name: 'refresh_token') required String refreshToken,
  }) = _SessionDto;

  factory SessionDto.fromJson(Map<String, dynamic> json) =>
      _$SessionDtoFromJson(json);

  Session toEntity() => Session(
        user: user.toEntity(),
        accessToken: accessToken,
        refreshToken: refreshToken,
      );
}

/// The `POST /auth/refresh` response — a fresh token pair, no user block.
@freezed
abstract class TokenPairDto with _$TokenPairDto {
  const factory TokenPairDto({
    @JsonKey(name: 'access_token') required String accessToken,
    @JsonKey(name: 'refresh_token') required String refreshToken,
  }) = _TokenPairDto;

  factory TokenPairDto.fromJson(Map<String, dynamic> json) =>
      _$TokenPairDtoFromJson(json);
}
