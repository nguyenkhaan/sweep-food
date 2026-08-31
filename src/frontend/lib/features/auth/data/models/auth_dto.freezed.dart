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
mixin _$UserDto {
  String get id;
  String get name;
  String get email;
  @JsonKey(name: 'dietary_preference')
  String? get dietaryPreference;
  @JsonKey(name: 'avatar_url')
  String? get avatarUrl;

  /// Create a copy of UserDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $UserDtoCopyWith<UserDto> get copyWith =>
      _$UserDtoCopyWithImpl<UserDto>(this as UserDto, _$identity);

  /// Serializes this UserDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is UserDto &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.dietaryPreference, dietaryPreference) ||
                other.dietaryPreference == dietaryPreference) &&
            (identical(other.avatarUrl, avatarUrl) ||
                other.avatarUrl == avatarUrl));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, id, name, email, dietaryPreference, avatarUrl);

  @override
  String toString() {
    return 'UserDto(id: $id, name: $name, email: $email, dietaryPreference: $dietaryPreference, avatarUrl: $avatarUrl)';
  }
}

/// @nodoc
abstract mixin class $UserDtoCopyWith<$Res> {
  factory $UserDtoCopyWith(UserDto value, $Res Function(UserDto) _then) =
      _$UserDtoCopyWithImpl;
  @useResult
  $Res call(
      {String id,
      String name,
      String email,
      @JsonKey(name: 'dietary_preference') String? dietaryPreference,
      @JsonKey(name: 'avatar_url') String? avatarUrl});
}

/// @nodoc
class _$UserDtoCopyWithImpl<$Res> implements $UserDtoCopyWith<$Res> {
  _$UserDtoCopyWithImpl(this._self, this._then);

  final UserDto _self;
  final $Res Function(UserDto) _then;

  /// Create a copy of UserDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? email = null,
    Object? dietaryPreference = freezed,
    Object? avatarUrl = freezed,
  }) {
    return _then(_self.copyWith(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      email: null == email
          ? _self.email
          : email // ignore: cast_nullable_to_non_nullable
              as String,
      dietaryPreference: freezed == dietaryPreference
          ? _self.dietaryPreference
          : dietaryPreference // ignore: cast_nullable_to_non_nullable
              as String?,
      avatarUrl: freezed == avatarUrl
          ? _self.avatarUrl
          : avatarUrl // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// Adds pattern-matching-related methods to [UserDto].
extension UserDtoPatterns on UserDto {
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

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>(
    TResult Function(_UserDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _UserDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult map<TResult extends Object?>(
    TResult Function(_UserDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _UserDto():
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>(
    TResult? Function(_UserDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _UserDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>(
    TResult Function(
            String id,
            String name,
            String email,
            @JsonKey(name: 'dietary_preference') String? dietaryPreference,
            @JsonKey(name: 'avatar_url') String? avatarUrl)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _UserDto() when $default != null:
        return $default(_that.id, _that.name, _that.email,
            _that.dietaryPreference, _that.avatarUrl);
      case _:
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

  @optionalTypeArgs
  TResult when<TResult extends Object?>(
    TResult Function(
            String id,
            String name,
            String email,
            @JsonKey(name: 'dietary_preference') String? dietaryPreference,
            @JsonKey(name: 'avatar_url') String? avatarUrl)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _UserDto():
        return $default(_that.id, _that.name, _that.email,
            _that.dietaryPreference, _that.avatarUrl);
      case _:
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

  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>(
    TResult? Function(
            String id,
            String name,
            String email,
            @JsonKey(name: 'dietary_preference') String? dietaryPreference,
            @JsonKey(name: 'avatar_url') String? avatarUrl)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _UserDto() when $default != null:
        return $default(_that.id, _that.name, _that.email,
            _that.dietaryPreference, _that.avatarUrl);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _UserDto extends UserDto {
  const _UserDto(
      {required this.id,
      required this.name,
      required this.email,
      @JsonKey(name: 'dietary_preference') this.dietaryPreference,
      @JsonKey(name: 'avatar_url') this.avatarUrl})
      : super._();
  factory _UserDto.fromJson(Map<String, dynamic> json) =>
      _$UserDtoFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String email;
  @override
  @JsonKey(name: 'dietary_preference')
  final String? dietaryPreference;
  @override
  @JsonKey(name: 'avatar_url')
  final String? avatarUrl;

  /// Create a copy of UserDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$UserDtoCopyWith<_UserDto> get copyWith =>
      __$UserDtoCopyWithImpl<_UserDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$UserDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _UserDto &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.dietaryPreference, dietaryPreference) ||
                other.dietaryPreference == dietaryPreference) &&
            (identical(other.avatarUrl, avatarUrl) ||
                other.avatarUrl == avatarUrl));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, id, name, email, dietaryPreference, avatarUrl);

  @override
  String toString() {
    return 'UserDto(id: $id, name: $name, email: $email, dietaryPreference: $dietaryPreference, avatarUrl: $avatarUrl)';
  }
}

/// @nodoc
abstract mixin class _$UserDtoCopyWith<$Res> implements $UserDtoCopyWith<$Res> {
  factory _$UserDtoCopyWith(_UserDto value, $Res Function(_UserDto) _then) =
      __$UserDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String email,
      @JsonKey(name: 'dietary_preference') String? dietaryPreference,
      @JsonKey(name: 'avatar_url') String? avatarUrl});
}

/// @nodoc
class __$UserDtoCopyWithImpl<$Res> implements _$UserDtoCopyWith<$Res> {
  __$UserDtoCopyWithImpl(this._self, this._then);

  final _UserDto _self;
  final $Res Function(_UserDto) _then;

  /// Create a copy of UserDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? email = null,
    Object? dietaryPreference = freezed,
    Object? avatarUrl = freezed,
  }) {
    return _then(_UserDto(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      email: null == email
          ? _self.email
          : email // ignore: cast_nullable_to_non_nullable
              as String,
      dietaryPreference: freezed == dietaryPreference
          ? _self.dietaryPreference
          : dietaryPreference // ignore: cast_nullable_to_non_nullable
              as String?,
      avatarUrl: freezed == avatarUrl
          ? _self.avatarUrl
          : avatarUrl // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
mixin _$SessionDto {
  UserDto get user;
  @JsonKey(name: 'access_token')
  String get accessToken;
  @JsonKey(name: 'refresh_token')
  String get refreshToken;

  /// Create a copy of SessionDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $SessionDtoCopyWith<SessionDto> get copyWith =>
      _$SessionDtoCopyWithImpl<SessionDto>(this as SessionDto, _$identity);

  /// Serializes this SessionDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is SessionDto &&
            (identical(other.user, user) || other.user == user) &&
            (identical(other.accessToken, accessToken) ||
                other.accessToken == accessToken) &&
            (identical(other.refreshToken, refreshToken) ||
                other.refreshToken == refreshToken));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, user, accessToken, refreshToken);

  @override
  String toString() {
    return 'SessionDto(user: $user, accessToken: $accessToken, refreshToken: $refreshToken)';
  }
}

/// @nodoc
abstract mixin class $SessionDtoCopyWith<$Res> {
  factory $SessionDtoCopyWith(
          SessionDto value, $Res Function(SessionDto) _then) =
      _$SessionDtoCopyWithImpl;
  @useResult
  $Res call(
      {UserDto user,
      @JsonKey(name: 'access_token') String accessToken,
      @JsonKey(name: 'refresh_token') String refreshToken});

  $UserDtoCopyWith<$Res> get user;
}

/// @nodoc
class _$SessionDtoCopyWithImpl<$Res> implements $SessionDtoCopyWith<$Res> {
  _$SessionDtoCopyWithImpl(this._self, this._then);

  final SessionDto _self;
  final $Res Function(SessionDto) _then;

  /// Create a copy of SessionDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? user = null,
    Object? accessToken = null,
    Object? refreshToken = null,
  }) {
    return _then(_self.copyWith(
      user: null == user
          ? _self.user
          : user // ignore: cast_nullable_to_non_nullable
              as UserDto,
      accessToken: null == accessToken
          ? _self.accessToken
          : accessToken // ignore: cast_nullable_to_non_nullable
              as String,
      refreshToken: null == refreshToken
          ? _self.refreshToken
          : refreshToken // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }

  /// Create a copy of SessionDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $UserDtoCopyWith<$Res> get user {
    return $UserDtoCopyWith<$Res>(_self.user, (value) {
      return _then(_self.copyWith(user: value));
    });
  }
}

/// Adds pattern-matching-related methods to [SessionDto].
extension SessionDtoPatterns on SessionDto {
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

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>(
    TResult Function(_SessionDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _SessionDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult map<TResult extends Object?>(
    TResult Function(_SessionDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _SessionDto():
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>(
    TResult? Function(_SessionDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _SessionDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>(
    TResult Function(
            UserDto user,
            @JsonKey(name: 'access_token') String accessToken,
            @JsonKey(name: 'refresh_token') String refreshToken)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _SessionDto() when $default != null:
        return $default(_that.user, _that.accessToken, _that.refreshToken);
      case _:
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

  @optionalTypeArgs
  TResult when<TResult extends Object?>(
    TResult Function(
            UserDto user,
            @JsonKey(name: 'access_token') String accessToken,
            @JsonKey(name: 'refresh_token') String refreshToken)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _SessionDto():
        return $default(_that.user, _that.accessToken, _that.refreshToken);
      case _:
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

  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>(
    TResult? Function(
            UserDto user,
            @JsonKey(name: 'access_token') String accessToken,
            @JsonKey(name: 'refresh_token') String refreshToken)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _SessionDto() when $default != null:
        return $default(_that.user, _that.accessToken, _that.refreshToken);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _SessionDto extends SessionDto {
  const _SessionDto(
      {required this.user,
      @JsonKey(name: 'access_token') required this.accessToken,
      @JsonKey(name: 'refresh_token') required this.refreshToken})
      : super._();
  factory _SessionDto.fromJson(Map<String, dynamic> json) =>
      _$SessionDtoFromJson(json);

  @override
  final UserDto user;
  @override
  @JsonKey(name: 'access_token')
  final String accessToken;
  @override
  @JsonKey(name: 'refresh_token')
  final String refreshToken;

  /// Create a copy of SessionDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$SessionDtoCopyWith<_SessionDto> get copyWith =>
      __$SessionDtoCopyWithImpl<_SessionDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$SessionDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _SessionDto &&
            (identical(other.user, user) || other.user == user) &&
            (identical(other.accessToken, accessToken) ||
                other.accessToken == accessToken) &&
            (identical(other.refreshToken, refreshToken) ||
                other.refreshToken == refreshToken));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, user, accessToken, refreshToken);

  @override
  String toString() {
    return 'SessionDto(user: $user, accessToken: $accessToken, refreshToken: $refreshToken)';
  }
}

/// @nodoc
abstract mixin class _$SessionDtoCopyWith<$Res>
    implements $SessionDtoCopyWith<$Res> {
  factory _$SessionDtoCopyWith(
          _SessionDto value, $Res Function(_SessionDto) _then) =
      __$SessionDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {UserDto user,
      @JsonKey(name: 'access_token') String accessToken,
      @JsonKey(name: 'refresh_token') String refreshToken});

  @override
  $UserDtoCopyWith<$Res> get user;
}

/// @nodoc
class __$SessionDtoCopyWithImpl<$Res> implements _$SessionDtoCopyWith<$Res> {
  __$SessionDtoCopyWithImpl(this._self, this._then);

  final _SessionDto _self;
  final $Res Function(_SessionDto) _then;

  /// Create a copy of SessionDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? user = null,
    Object? accessToken = null,
    Object? refreshToken = null,
  }) {
    return _then(_SessionDto(
      user: null == user
          ? _self.user
          : user // ignore: cast_nullable_to_non_nullable
              as UserDto,
      accessToken: null == accessToken
          ? _self.accessToken
          : accessToken // ignore: cast_nullable_to_non_nullable
              as String,
      refreshToken: null == refreshToken
          ? _self.refreshToken
          : refreshToken // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }

  /// Create a copy of SessionDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $UserDtoCopyWith<$Res> get user {
    return $UserDtoCopyWith<$Res>(_self.user, (value) {
      return _then(_self.copyWith(user: value));
    });
  }
}

/// @nodoc
mixin _$TokenPairDto {
  @JsonKey(name: 'access_token')
  String get accessToken;
  @JsonKey(name: 'refresh_token')
  String get refreshToken;

  /// Create a copy of TokenPairDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $TokenPairDtoCopyWith<TokenPairDto> get copyWith =>
      _$TokenPairDtoCopyWithImpl<TokenPairDto>(
          this as TokenPairDto, _$identity);

  /// Serializes this TokenPairDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is TokenPairDto &&
            (identical(other.accessToken, accessToken) ||
                other.accessToken == accessToken) &&
            (identical(other.refreshToken, refreshToken) ||
                other.refreshToken == refreshToken));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, accessToken, refreshToken);

  @override
  String toString() {
    return 'TokenPairDto(accessToken: $accessToken, refreshToken: $refreshToken)';
  }
}

/// @nodoc
abstract mixin class $TokenPairDtoCopyWith<$Res> {
  factory $TokenPairDtoCopyWith(
          TokenPairDto value, $Res Function(TokenPairDto) _then) =
      _$TokenPairDtoCopyWithImpl;
  @useResult
  $Res call(
      {@JsonKey(name: 'access_token') String accessToken,
      @JsonKey(name: 'refresh_token') String refreshToken});
}

/// @nodoc
class _$TokenPairDtoCopyWithImpl<$Res> implements $TokenPairDtoCopyWith<$Res> {
  _$TokenPairDtoCopyWithImpl(this._self, this._then);

  final TokenPairDto _self;
  final $Res Function(TokenPairDto) _then;

  /// Create a copy of TokenPairDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? accessToken = null,
    Object? refreshToken = null,
  }) {
    return _then(_self.copyWith(
      accessToken: null == accessToken
          ? _self.accessToken
          : accessToken // ignore: cast_nullable_to_non_nullable
              as String,
      refreshToken: null == refreshToken
          ? _self.refreshToken
          : refreshToken // ignore: cast_nullable_to_non_nullable
              as String,
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

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>(
    TResult Function(_TokenPairDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _TokenPairDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult map<TResult extends Object?>(
    TResult Function(_TokenPairDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _TokenPairDto():
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>(
    TResult? Function(_TokenPairDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _TokenPairDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>(
    TResult Function(@JsonKey(name: 'access_token') String accessToken,
            @JsonKey(name: 'refresh_token') String refreshToken)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _TokenPairDto() when $default != null:
        return $default(_that.accessToken, _that.refreshToken);
      case _:
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

  @optionalTypeArgs
  TResult when<TResult extends Object?>(
    TResult Function(@JsonKey(name: 'access_token') String accessToken,
            @JsonKey(name: 'refresh_token') String refreshToken)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _TokenPairDto():
        return $default(_that.accessToken, _that.refreshToken);
      case _:
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

  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>(
    TResult? Function(@JsonKey(name: 'access_token') String accessToken,
            @JsonKey(name: 'refresh_token') String refreshToken)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _TokenPairDto() when $default != null:
        return $default(_that.accessToken, _that.refreshToken);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _TokenPairDto implements TokenPairDto {
  const _TokenPairDto(
      {@JsonKey(name: 'access_token') required this.accessToken,
      @JsonKey(name: 'refresh_token') required this.refreshToken});
  factory _TokenPairDto.fromJson(Map<String, dynamic> json) =>
      _$TokenPairDtoFromJson(json);

  @override
  @JsonKey(name: 'access_token')
  final String accessToken;
  @override
  @JsonKey(name: 'refresh_token')
  final String refreshToken;

  /// Create a copy of TokenPairDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$TokenPairDtoCopyWith<_TokenPairDto> get copyWith =>
      __$TokenPairDtoCopyWithImpl<_TokenPairDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$TokenPairDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _TokenPairDto &&
            (identical(other.accessToken, accessToken) ||
                other.accessToken == accessToken) &&
            (identical(other.refreshToken, refreshToken) ||
                other.refreshToken == refreshToken));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, accessToken, refreshToken);

  @override
  String toString() {
    return 'TokenPairDto(accessToken: $accessToken, refreshToken: $refreshToken)';
  }
}

/// @nodoc
abstract mixin class _$TokenPairDtoCopyWith<$Res>
    implements $TokenPairDtoCopyWith<$Res> {
  factory _$TokenPairDtoCopyWith(
          _TokenPairDto value, $Res Function(_TokenPairDto) _then) =
      __$TokenPairDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'access_token') String accessToken,
      @JsonKey(name: 'refresh_token') String refreshToken});
}

/// @nodoc
class __$TokenPairDtoCopyWithImpl<$Res>
    implements _$TokenPairDtoCopyWith<$Res> {
  __$TokenPairDtoCopyWithImpl(this._self, this._then);

  final _TokenPairDto _self;
  final $Res Function(_TokenPairDto) _then;

  /// Create a copy of TokenPairDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? accessToken = null,
    Object? refreshToken = null,
  }) {
    return _then(_TokenPairDto(
      accessToken: null == accessToken
          ? _self.accessToken
          : accessToken // ignore: cast_nullable_to_non_nullable
              as String,
      refreshToken: null == refreshToken
          ? _self.refreshToken
          : refreshToken // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

// dart format on
