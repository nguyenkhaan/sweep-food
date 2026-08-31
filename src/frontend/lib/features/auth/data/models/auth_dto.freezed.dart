// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'auth_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$OtpIssueDto {

 String get otp;@JsonKey(name: 'expires_in_seconds') int get expiresInSeconds;
/// Create a copy of OtpIssueDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OtpIssueDtoCopyWith<OtpIssueDto> get copyWith => _$OtpIssueDtoCopyWithImpl<OtpIssueDto>(this as OtpIssueDto, _$identity);

  /// Serializes this OtpIssueDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is OtpIssueDto&&(identical(other.otp, otp) || other.otp == otp)&&(identical(other.expiresInSeconds, expiresInSeconds) || other.expiresInSeconds == expiresInSeconds));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,otp,expiresInSeconds);

@override
String toString() {
  return 'OtpIssueDto(otp: $otp, expiresInSeconds: $expiresInSeconds)';
}


}

/// @nodoc
abstract mixin class $OtpIssueDtoCopyWith<$Res>  {
  factory $OtpIssueDtoCopyWith(OtpIssueDto value, $Res Function(OtpIssueDto) _then) = _$OtpIssueDtoCopyWithImpl;
@useResult
$Res call({
 String otp,@JsonKey(name: 'expires_in_seconds') int expiresInSeconds
});




}
/// @nodoc
class _$OtpIssueDtoCopyWithImpl<$Res>
    implements $OtpIssueDtoCopyWith<$Res> {
  _$OtpIssueDtoCopyWithImpl(this._self, this._then);

  final OtpIssueDto _self;
  final $Res Function(OtpIssueDto) _then;

/// Create a copy of OtpIssueDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? otp = null,Object? expiresInSeconds = null,}) {
  return _then(_self.copyWith(
otp: null == otp ? _self.otp : otp // ignore: cast_nullable_to_non_nullable
as String,expiresInSeconds: null == expiresInSeconds ? _self.expiresInSeconds : expiresInSeconds // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [OtpIssueDto].
extension OtpIssueDtoPatterns on OtpIssueDto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OtpIssueDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OtpIssueDto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OtpIssueDto value)  $default,){
final _that = this;
switch (_that) {
case _OtpIssueDto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OtpIssueDto value)?  $default,){
final _that = this;
switch (_that) {
case _OtpIssueDto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String otp, @JsonKey(name: 'expires_in_seconds')  int expiresInSeconds)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OtpIssueDto() when $default != null:
return $default(_that.otp,_that.expiresInSeconds);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String otp, @JsonKey(name: 'expires_in_seconds')  int expiresInSeconds)  $default,) {final _that = this;
switch (_that) {
case _OtpIssueDto():
return $default(_that.otp,_that.expiresInSeconds);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String otp, @JsonKey(name: 'expires_in_seconds')  int expiresInSeconds)?  $default,) {final _that = this;
switch (_that) {
case _OtpIssueDto() when $default != null:
return $default(_that.otp,_that.expiresInSeconds);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OtpIssueDto implements OtpIssueDto {
  const _OtpIssueDto({required this.otp, @JsonKey(name: 'expires_in_seconds') required this.expiresInSeconds});
  factory _OtpIssueDto.fromJson(Map<String, dynamic> json) => _$OtpIssueDtoFromJson(json);

@override final  String otp;
@override@JsonKey(name: 'expires_in_seconds') final  int expiresInSeconds;

/// Create a copy of OtpIssueDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OtpIssueDtoCopyWith<_OtpIssueDto> get copyWith => __$OtpIssueDtoCopyWithImpl<_OtpIssueDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OtpIssueDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _OtpIssueDto&&(identical(other.otp, otp) || other.otp == otp)&&(identical(other.expiresInSeconds, expiresInSeconds) || other.expiresInSeconds == expiresInSeconds));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,otp,expiresInSeconds);

@override
String toString() {
  return 'OtpIssueDto(otp: $otp, expiresInSeconds: $expiresInSeconds)';
}


}

/// @nodoc
abstract mixin class _$OtpIssueDtoCopyWith<$Res> implements $OtpIssueDtoCopyWith<$Res> {
  factory _$OtpIssueDtoCopyWith(_OtpIssueDto value, $Res Function(_OtpIssueDto) _then) = __$OtpIssueDtoCopyWithImpl;
@override @useResult
$Res call({
 String otp,@JsonKey(name: 'expires_in_seconds') int expiresInSeconds
});




}
/// @nodoc
class __$OtpIssueDtoCopyWithImpl<$Res>
    implements _$OtpIssueDtoCopyWith<$Res> {
  __$OtpIssueDtoCopyWithImpl(this._self, this._then);

  final _OtpIssueDto _self;
  final $Res Function(_OtpIssueDto) _then;

/// Create a copy of OtpIssueDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? otp = null,Object? expiresInSeconds = null,}) {
  return _then(_OtpIssueDto(
otp: null == otp ? _self.otp : otp // ignore: cast_nullable_to_non_nullable
as String,expiresInSeconds: null == expiresInSeconds ? _self.expiresInSeconds : expiresInSeconds // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$TokenPairDto {

@JsonKey(name: 'access_token') String get accessToken;@JsonKey(name: 'refresh_token') String get refreshToken;@JsonKey(name: 'token_type') String? get tokenType;@JsonKey(name: 'access_expires_in_seconds') int? get accessExpiresInSeconds;@JsonKey(name: 'refresh_expires_in_seconds') int? get refreshExpiresInSeconds;@JsonKey(name: 'session_id') String? get sessionId;
/// Create a copy of TokenPairDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TokenPairDtoCopyWith<TokenPairDto> get copyWith => _$TokenPairDtoCopyWithImpl<TokenPairDto>(this as TokenPairDto, _$identity);

  /// Serializes this TokenPairDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is TokenPairDto&&(identical(other.accessToken, accessToken) || other.accessToken == accessToken)&&(identical(other.refreshToken, refreshToken) || other.refreshToken == refreshToken)&&(identical(other.tokenType, tokenType) || other.tokenType == tokenType)&&(identical(other.accessExpiresInSeconds, accessExpiresInSeconds) || other.accessExpiresInSeconds == accessExpiresInSeconds)&&(identical(other.refreshExpiresInSeconds, refreshExpiresInSeconds) || other.refreshExpiresInSeconds == refreshExpiresInSeconds)&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,accessToken,refreshToken,tokenType,accessExpiresInSeconds,refreshExpiresInSeconds,sessionId);

@override
String toString() {
  return 'TokenPairDto(accessToken: $accessToken, refreshToken: $refreshToken, tokenType: $tokenType, accessExpiresInSeconds: $accessExpiresInSeconds, refreshExpiresInSeconds: $refreshExpiresInSeconds, sessionId: $sessionId)';
}


}

/// @nodoc
abstract mixin class $TokenPairDtoCopyWith<$Res>  {
  factory $TokenPairDtoCopyWith(TokenPairDto value, $Res Function(TokenPairDto) _then) = _$TokenPairDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'access_token') String accessToken,@JsonKey(name: 'refresh_token') String refreshToken,@JsonKey(name: 'token_type') String? tokenType,@JsonKey(name: 'access_expires_in_seconds') int? accessExpiresInSeconds,@JsonKey(name: 'refresh_expires_in_seconds') int? refreshExpiresInSeconds,@JsonKey(name: 'session_id') String? sessionId
});




}
/// @nodoc
class _$TokenPairDtoCopyWithImpl<$Res>
    implements $TokenPairDtoCopyWith<$Res> {
  _$TokenPairDtoCopyWithImpl(this._self, this._then);

  final TokenPairDto _self;
  final $Res Function(TokenPairDto) _then;

/// Create a copy of TokenPairDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? accessToken = null,Object? refreshToken = null,Object? tokenType = freezed,Object? accessExpiresInSeconds = freezed,Object? refreshExpiresInSeconds = freezed,Object? sessionId = freezed,}) {
  return _then(_self.copyWith(
accessToken: null == accessToken ? _self.accessToken : accessToken // ignore: cast_nullable_to_non_nullable
as String,refreshToken: null == refreshToken ? _self.refreshToken : refreshToken // ignore: cast_nullable_to_non_nullable
as String,tokenType: freezed == tokenType ? _self.tokenType : tokenType // ignore: cast_nullable_to_non_nullable
as String?,accessExpiresInSeconds: freezed == accessExpiresInSeconds ? _self.accessExpiresInSeconds : accessExpiresInSeconds // ignore: cast_nullable_to_non_nullable
as int?,refreshExpiresInSeconds: freezed == refreshExpiresInSeconds ? _self.refreshExpiresInSeconds : refreshExpiresInSeconds // ignore: cast_nullable_to_non_nullable
as int?,sessionId: freezed == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [TokenPairDto].
extension TokenPairDtoPatterns on TokenPairDto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TokenPairDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TokenPairDto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TokenPairDto value)  $default,){
final _that = this;
switch (_that) {
case _TokenPairDto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TokenPairDto value)?  $default,){
final _that = this;
switch (_that) {
case _TokenPairDto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'refresh_token')  String refreshToken, @JsonKey(name: 'token_type')  String? tokenType, @JsonKey(name: 'access_expires_in_seconds')  int? accessExpiresInSeconds, @JsonKey(name: 'refresh_expires_in_seconds')  int? refreshExpiresInSeconds, @JsonKey(name: 'session_id')  String? sessionId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TokenPairDto() when $default != null:
return $default(_that.accessToken,_that.refreshToken,_that.tokenType,_that.accessExpiresInSeconds,_that.refreshExpiresInSeconds,_that.sessionId);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'refresh_token')  String refreshToken, @JsonKey(name: 'token_type')  String? tokenType, @JsonKey(name: 'access_expires_in_seconds')  int? accessExpiresInSeconds, @JsonKey(name: 'refresh_expires_in_seconds')  int? refreshExpiresInSeconds, @JsonKey(name: 'session_id')  String? sessionId)  $default,) {final _that = this;
switch (_that) {
case _TokenPairDto():
return $default(_that.accessToken,_that.refreshToken,_that.tokenType,_that.accessExpiresInSeconds,_that.refreshExpiresInSeconds,_that.sessionId);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'refresh_token')  String refreshToken, @JsonKey(name: 'token_type')  String? tokenType, @JsonKey(name: 'access_expires_in_seconds')  int? accessExpiresInSeconds, @JsonKey(name: 'refresh_expires_in_seconds')  int? refreshExpiresInSeconds, @JsonKey(name: 'session_id')  String? sessionId)?  $default,) {final _that = this;
switch (_that) {
case _TokenPairDto() when $default != null:
return $default(_that.accessToken,_that.refreshToken,_that.tokenType,_that.accessExpiresInSeconds,_that.refreshExpiresInSeconds,_that.sessionId);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _TokenPairDto implements TokenPairDto {
  const _TokenPairDto({@JsonKey(name: 'access_token') required this.accessToken, @JsonKey(name: 'refresh_token') required this.refreshToken, @JsonKey(name: 'token_type') this.tokenType, @JsonKey(name: 'access_expires_in_seconds') this.accessExpiresInSeconds, @JsonKey(name: 'refresh_expires_in_seconds') this.refreshExpiresInSeconds, @JsonKey(name: 'session_id') this.sessionId});
  factory _TokenPairDto.fromJson(Map<String, dynamic> json) => _$TokenPairDtoFromJson(json);

@override@JsonKey(name: 'access_token') final  String accessToken;
@override@JsonKey(name: 'refresh_token') final  String refreshToken;
@override@JsonKey(name: 'token_type') final  String? tokenType;
@override@JsonKey(name: 'access_expires_in_seconds') final  int? accessExpiresInSeconds;
@override@JsonKey(name: 'refresh_expires_in_seconds') final  int? refreshExpiresInSeconds;
@override@JsonKey(name: 'session_id') final  String? sessionId;

/// Create a copy of TokenPairDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TokenPairDtoCopyWith<_TokenPairDto> get copyWith => __$TokenPairDtoCopyWithImpl<_TokenPairDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TokenPairDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _TokenPairDto&&(identical(other.accessToken, accessToken) || other.accessToken == accessToken)&&(identical(other.refreshToken, refreshToken) || other.refreshToken == refreshToken)&&(identical(other.tokenType, tokenType) || other.tokenType == tokenType)&&(identical(other.accessExpiresInSeconds, accessExpiresInSeconds) || other.accessExpiresInSeconds == accessExpiresInSeconds)&&(identical(other.refreshExpiresInSeconds, refreshExpiresInSeconds) || other.refreshExpiresInSeconds == refreshExpiresInSeconds)&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,accessToken,refreshToken,tokenType,accessExpiresInSeconds,refreshExpiresInSeconds,sessionId);

@override
String toString() {
  return 'TokenPairDto(accessToken: $accessToken, refreshToken: $refreshToken, tokenType: $tokenType, accessExpiresInSeconds: $accessExpiresInSeconds, refreshExpiresInSeconds: $refreshExpiresInSeconds, sessionId: $sessionId)';
}


}

/// @nodoc
abstract mixin class _$TokenPairDtoCopyWith<$Res> implements $TokenPairDtoCopyWith<$Res> {
  factory _$TokenPairDtoCopyWith(_TokenPairDto value, $Res Function(_TokenPairDto) _then) = __$TokenPairDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'access_token') String accessToken,@JsonKey(name: 'refresh_token') String refreshToken,@JsonKey(name: 'token_type') String? tokenType,@JsonKey(name: 'access_expires_in_seconds') int? accessExpiresInSeconds,@JsonKey(name: 'refresh_expires_in_seconds') int? refreshExpiresInSeconds,@JsonKey(name: 'session_id') String? sessionId
});




}
/// @nodoc
class __$TokenPairDtoCopyWithImpl<$Res>
    implements _$TokenPairDtoCopyWith<$Res> {
  __$TokenPairDtoCopyWithImpl(this._self, this._then);

  final _TokenPairDto _self;
  final $Res Function(_TokenPairDto) _then;

/// Create a copy of TokenPairDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? accessToken = null,Object? refreshToken = null,Object? tokenType = freezed,Object? accessExpiresInSeconds = freezed,Object? refreshExpiresInSeconds = freezed,Object? sessionId = freezed,}) {
  return _then(_TokenPairDto(
accessToken: null == accessToken ? _self.accessToken : accessToken // ignore: cast_nullable_to_non_nullable
as String,refreshToken: null == refreshToken ? _self.refreshToken : refreshToken // ignore: cast_nullable_to_non_nullable
as String,tokenType: freezed == tokenType ? _self.tokenType : tokenType // ignore: cast_nullable_to_non_nullable
as String?,accessExpiresInSeconds: freezed == accessExpiresInSeconds ? _self.accessExpiresInSeconds : accessExpiresInSeconds // ignore: cast_nullable_to_non_nullable
as int?,refreshExpiresInSeconds: freezed == refreshExpiresInSeconds ? _self.refreshExpiresInSeconds : refreshExpiresInSeconds // ignore: cast_nullable_to_non_nullable
as int?,sessionId: freezed == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$AccessTokenDto {

@JsonKey(name: 'access_token') String get accessToken;@JsonKey(name: 'token_type') String? get tokenType;@JsonKey(name: 'access_expires_in_seconds') int? get accessExpiresInSeconds;
/// Create a copy of AccessTokenDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AccessTokenDtoCopyWith<AccessTokenDto> get copyWith => _$AccessTokenDtoCopyWithImpl<AccessTokenDto>(this as AccessTokenDto, _$identity);

  /// Serializes this AccessTokenDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AccessTokenDto&&(identical(other.accessToken, accessToken) || other.accessToken == accessToken)&&(identical(other.tokenType, tokenType) || other.tokenType == tokenType)&&(identical(other.accessExpiresInSeconds, accessExpiresInSeconds) || other.accessExpiresInSeconds == accessExpiresInSeconds));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,accessToken,tokenType,accessExpiresInSeconds);

@override
String toString() {
  return 'AccessTokenDto(accessToken: $accessToken, tokenType: $tokenType, accessExpiresInSeconds: $accessExpiresInSeconds)';
}


}

/// @nodoc
abstract mixin class $AccessTokenDtoCopyWith<$Res>  {
  factory $AccessTokenDtoCopyWith(AccessTokenDto value, $Res Function(AccessTokenDto) _then) = _$AccessTokenDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'access_token') String accessToken,@JsonKey(name: 'token_type') String? tokenType,@JsonKey(name: 'access_expires_in_seconds') int? accessExpiresInSeconds
});




}
/// @nodoc
class _$AccessTokenDtoCopyWithImpl<$Res>
    implements $AccessTokenDtoCopyWith<$Res> {
  _$AccessTokenDtoCopyWithImpl(this._self, this._then);

  final AccessTokenDto _self;
  final $Res Function(AccessTokenDto) _then;

/// Create a copy of AccessTokenDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? accessToken = null,Object? tokenType = freezed,Object? accessExpiresInSeconds = freezed,}) {
  return _then(_self.copyWith(
accessToken: null == accessToken ? _self.accessToken : accessToken // ignore: cast_nullable_to_non_nullable
as String,tokenType: freezed == tokenType ? _self.tokenType : tokenType // ignore: cast_nullable_to_non_nullable
as String?,accessExpiresInSeconds: freezed == accessExpiresInSeconds ? _self.accessExpiresInSeconds : accessExpiresInSeconds // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [AccessTokenDto].
extension AccessTokenDtoPatterns on AccessTokenDto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AccessTokenDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AccessTokenDto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AccessTokenDto value)  $default,){
final _that = this;
switch (_that) {
case _AccessTokenDto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AccessTokenDto value)?  $default,){
final _that = this;
switch (_that) {
case _AccessTokenDto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'token_type')  String? tokenType, @JsonKey(name: 'access_expires_in_seconds')  int? accessExpiresInSeconds)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AccessTokenDto() when $default != null:
return $default(_that.accessToken,_that.tokenType,_that.accessExpiresInSeconds);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'token_type')  String? tokenType, @JsonKey(name: 'access_expires_in_seconds')  int? accessExpiresInSeconds)  $default,) {final _that = this;
switch (_that) {
case _AccessTokenDto():
return $default(_that.accessToken,_that.tokenType,_that.accessExpiresInSeconds);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'token_type')  String? tokenType, @JsonKey(name: 'access_expires_in_seconds')  int? accessExpiresInSeconds)?  $default,) {final _that = this;
switch (_that) {
case _AccessTokenDto() when $default != null:
return $default(_that.accessToken,_that.tokenType,_that.accessExpiresInSeconds);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AccessTokenDto implements AccessTokenDto {
  const _AccessTokenDto({@JsonKey(name: 'access_token') required this.accessToken, @JsonKey(name: 'token_type') this.tokenType, @JsonKey(name: 'access_expires_in_seconds') this.accessExpiresInSeconds});
  factory _AccessTokenDto.fromJson(Map<String, dynamic> json) => _$AccessTokenDtoFromJson(json);

@override@JsonKey(name: 'access_token') final  String accessToken;
@override@JsonKey(name: 'token_type') final  String? tokenType;
@override@JsonKey(name: 'access_expires_in_seconds') final  int? accessExpiresInSeconds;

/// Create a copy of AccessTokenDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AccessTokenDtoCopyWith<_AccessTokenDto> get copyWith => __$AccessTokenDtoCopyWithImpl<_AccessTokenDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AccessTokenDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _AccessTokenDto&&(identical(other.accessToken, accessToken) || other.accessToken == accessToken)&&(identical(other.tokenType, tokenType) || other.tokenType == tokenType)&&(identical(other.accessExpiresInSeconds, accessExpiresInSeconds) || other.accessExpiresInSeconds == accessExpiresInSeconds));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,accessToken,tokenType,accessExpiresInSeconds);

@override
String toString() {
  return 'AccessTokenDto(accessToken: $accessToken, tokenType: $tokenType, accessExpiresInSeconds: $accessExpiresInSeconds)';
}


}

/// @nodoc
abstract mixin class _$AccessTokenDtoCopyWith<$Res> implements $AccessTokenDtoCopyWith<$Res> {
  factory _$AccessTokenDtoCopyWith(_AccessTokenDto value, $Res Function(_AccessTokenDto) _then) = __$AccessTokenDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'access_token') String accessToken,@JsonKey(name: 'token_type') String? tokenType,@JsonKey(name: 'access_expires_in_seconds') int? accessExpiresInSeconds
});




}
/// @nodoc
class __$AccessTokenDtoCopyWithImpl<$Res>
    implements _$AccessTokenDtoCopyWith<$Res> {
  __$AccessTokenDtoCopyWithImpl(this._self, this._then);

  final _AccessTokenDto _self;
  final $Res Function(_AccessTokenDto) _then;

/// Create a copy of AccessTokenDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? accessToken = null,Object? tokenType = freezed,Object? accessExpiresInSeconds = freezed,}) {
  return _then(_AccessTokenDto(
accessToken: null == accessToken ? _self.accessToken : accessToken // ignore: cast_nullable_to_non_nullable
as String,tokenType: freezed == tokenType ? _self.tokenType : tokenType // ignore: cast_nullable_to_non_nullable
as String?,accessExpiresInSeconds: freezed == accessExpiresInSeconds ? _self.accessExpiresInSeconds : accessExpiresInSeconds // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}


/// @nodoc
mixin _$UserProfileDto {

@JsonKey(name: 'user_id') String get userId; String? get name; String get phone;@JsonKey(name: 'phone_verified_at') String? get phoneVerifiedAt; String? get email;@JsonKey(name: 'email_verified_at') String? get emailVerifiedAt; Map<String, dynamic> get preferences;
/// Create a copy of UserProfileDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserProfileDtoCopyWith<UserProfileDto> get copyWith => _$UserProfileDtoCopyWithImpl<UserProfileDto>(this as UserProfileDto, _$identity);

  /// Serializes this UserProfileDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserProfileDto&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.name, name) || other.name == name)&&(identical(other.phone, phone) || other.phone == phone)&&(identical(other.phoneVerifiedAt, phoneVerifiedAt) || other.phoneVerifiedAt == phoneVerifiedAt)&&(identical(other.email, email) || other.email == email)&&(identical(other.emailVerifiedAt, emailVerifiedAt) || other.emailVerifiedAt == emailVerifiedAt)&&const DeepCollectionEquality().equals(other.preferences, preferences));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,userId,name,phone,phoneVerifiedAt,email,emailVerifiedAt,const DeepCollectionEquality().hash(preferences));

@override
String toString() {
  return 'UserProfileDto(userId: $userId, name: $name, phone: $phone, phoneVerifiedAt: $phoneVerifiedAt, email: $email, emailVerifiedAt: $emailVerifiedAt, preferences: $preferences)';
}


}

/// @nodoc
abstract mixin class $UserProfileDtoCopyWith<$Res>  {
  factory $UserProfileDtoCopyWith(UserProfileDto value, $Res Function(UserProfileDto) _then) = _$UserProfileDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'user_id') String userId, String? name, String phone,@JsonKey(name: 'phone_verified_at') String? phoneVerifiedAt, String? email,@JsonKey(name: 'email_verified_at') String? emailVerifiedAt, Map<String, dynamic> preferences
});




}
/// @nodoc
class _$UserProfileDtoCopyWithImpl<$Res>
    implements $UserProfileDtoCopyWith<$Res> {
  _$UserProfileDtoCopyWithImpl(this._self, this._then);

  final UserProfileDto _self;
  final $Res Function(UserProfileDto) _then;

/// Create a copy of UserProfileDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? userId = null,Object? name = freezed,Object? phone = null,Object? phoneVerifiedAt = freezed,Object? email = freezed,Object? emailVerifiedAt = freezed,Object? preferences = null,}) {
  return _then(_self.copyWith(
userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,phoneVerifiedAt: freezed == phoneVerifiedAt ? _self.phoneVerifiedAt : phoneVerifiedAt // ignore: cast_nullable_to_non_nullable
as String?,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,emailVerifiedAt: freezed == emailVerifiedAt ? _self.emailVerifiedAt : emailVerifiedAt // ignore: cast_nullable_to_non_nullable
as String?,preferences: null == preferences ? _self.preferences : preferences // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [UserProfileDto].
extension UserProfileDtoPatterns on UserProfileDto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserProfileDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserProfileDto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserProfileDto value)  $default,){
final _that = this;
switch (_that) {
case _UserProfileDto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserProfileDto value)?  $default,){
final _that = this;
switch (_that) {
case _UserProfileDto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'user_id')  String userId,  String? name,  String phone, @JsonKey(name: 'phone_verified_at')  String? phoneVerifiedAt,  String? email, @JsonKey(name: 'email_verified_at')  String? emailVerifiedAt,  Map<String, dynamic> preferences)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserProfileDto() when $default != null:
return $default(_that.userId,_that.name,_that.phone,_that.phoneVerifiedAt,_that.email,_that.emailVerifiedAt,_that.preferences);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'user_id')  String userId,  String? name,  String phone, @JsonKey(name: 'phone_verified_at')  String? phoneVerifiedAt,  String? email, @JsonKey(name: 'email_verified_at')  String? emailVerifiedAt,  Map<String, dynamic> preferences)  $default,) {final _that = this;
switch (_that) {
case _UserProfileDto():
return $default(_that.userId,_that.name,_that.phone,_that.phoneVerifiedAt,_that.email,_that.emailVerifiedAt,_that.preferences);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'user_id')  String userId,  String? name,  String phone, @JsonKey(name: 'phone_verified_at')  String? phoneVerifiedAt,  String? email, @JsonKey(name: 'email_verified_at')  String? emailVerifiedAt,  Map<String, dynamic> preferences)?  $default,) {final _that = this;
switch (_that) {
case _UserProfileDto() when $default != null:
return $default(_that.userId,_that.name,_that.phone,_that.phoneVerifiedAt,_that.email,_that.emailVerifiedAt,_that.preferences);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UserProfileDto extends UserProfileDto {
  const _UserProfileDto({@JsonKey(name: 'user_id') required this.userId, this.name, required this.phone, @JsonKey(name: 'phone_verified_at') this.phoneVerifiedAt, this.email, @JsonKey(name: 'email_verified_at') this.emailVerifiedAt, final  Map<String, dynamic> preferences = const <String, dynamic>{}}): _preferences = preferences,super._();
  factory _UserProfileDto.fromJson(Map<String, dynamic> json) => _$UserProfileDtoFromJson(json);

@override@JsonKey(name: 'user_id') final  String userId;
@override final  String? name;
@override final  String phone;
@override@JsonKey(name: 'phone_verified_at') final  String? phoneVerifiedAt;
@override final  String? email;
@override@JsonKey(name: 'email_verified_at') final  String? emailVerifiedAt;
 final  Map<String, dynamic> _preferences;
@override@JsonKey() Map<String, dynamic> get preferences {
  if (_preferences is EqualUnmodifiableMapView) return _preferences;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_preferences);
}


/// Create a copy of UserProfileDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserProfileDtoCopyWith<_UserProfileDto> get copyWith => __$UserProfileDtoCopyWithImpl<_UserProfileDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserProfileDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserProfileDto&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.name, name) || other.name == name)&&(identical(other.phone, phone) || other.phone == phone)&&(identical(other.phoneVerifiedAt, phoneVerifiedAt) || other.phoneVerifiedAt == phoneVerifiedAt)&&(identical(other.email, email) || other.email == email)&&(identical(other.emailVerifiedAt, emailVerifiedAt) || other.emailVerifiedAt == emailVerifiedAt)&&const DeepCollectionEquality().equals(other._preferences, _preferences));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,userId,name,phone,phoneVerifiedAt,email,emailVerifiedAt,const DeepCollectionEquality().hash(_preferences));

@override
String toString() {
  return 'UserProfileDto(userId: $userId, name: $name, phone: $phone, phoneVerifiedAt: $phoneVerifiedAt, email: $email, emailVerifiedAt: $emailVerifiedAt, preferences: $preferences)';
}


}

/// @nodoc
abstract mixin class _$UserProfileDtoCopyWith<$Res> implements $UserProfileDtoCopyWith<$Res> {
  factory _$UserProfileDtoCopyWith(_UserProfileDto value, $Res Function(_UserProfileDto) _then) = __$UserProfileDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'user_id') String userId, String? name, String phone,@JsonKey(name: 'phone_verified_at') String? phoneVerifiedAt, String? email,@JsonKey(name: 'email_verified_at') String? emailVerifiedAt, Map<String, dynamic> preferences
});




}
/// @nodoc
class __$UserProfileDtoCopyWithImpl<$Res>
    implements _$UserProfileDtoCopyWith<$Res> {
  __$UserProfileDtoCopyWithImpl(this._self, this._then);

  final _UserProfileDto _self;
  final $Res Function(_UserProfileDto) _then;

/// Create a copy of UserProfileDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? userId = null,Object? name = freezed,Object? phone = null,Object? phoneVerifiedAt = freezed,Object? email = freezed,Object? emailVerifiedAt = freezed,Object? preferences = null,}) {
  return _then(_UserProfileDto(
userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,phoneVerifiedAt: freezed == phoneVerifiedAt ? _self.phoneVerifiedAt : phoneVerifiedAt // ignore: cast_nullable_to_non_nullable
as String?,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,emailVerifiedAt: freezed == emailVerifiedAt ? _self.emailVerifiedAt : emailVerifiedAt // ignore: cast_nullable_to_non_nullable
as String?,preferences: null == preferences ? _self._preferences : preferences // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
