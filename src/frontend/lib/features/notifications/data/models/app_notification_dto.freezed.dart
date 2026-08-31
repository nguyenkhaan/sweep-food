// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'app_notification_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$AppNotificationDto {
  String get id;
  String get type;
  String get title;
  String get body;
  @JsonKey(name: 'created_at')
  DateTime get createdAt;
  bool get read;
  @JsonKey(name: 'pantry_item_id')
  String? get pantryItemId;
  @JsonKey(name: 'dish_ids')
  List<String> get dishIds;

  /// Create a copy of AppNotificationDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $AppNotificationDtoCopyWith<AppNotificationDto> get copyWith =>
      _$AppNotificationDtoCopyWithImpl<AppNotificationDto>(
          this as AppNotificationDto, _$identity);

  /// Serializes this AppNotificationDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is AppNotificationDto &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.body, body) || other.body == body) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.read, read) || other.read == read) &&
            (identical(other.pantryItemId, pantryItemId) ||
                other.pantryItemId == pantryItemId) &&
            const DeepCollectionEquality().equals(other.dishIds, dishIds));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, type, title, body, createdAt,
      read, pantryItemId, const DeepCollectionEquality().hash(dishIds));

  @override
  String toString() {
    return 'AppNotificationDto(id: $id, type: $type, title: $title, body: $body, createdAt: $createdAt, read: $read, pantryItemId: $pantryItemId, dishIds: $dishIds)';
  }
}

/// @nodoc
abstract mixin class $AppNotificationDtoCopyWith<$Res> {
  factory $AppNotificationDtoCopyWith(
          AppNotificationDto value, $Res Function(AppNotificationDto) _then) =
      _$AppNotificationDtoCopyWithImpl;
  @useResult
  $Res call(
      {String id,
      String type,
      String title,
      String body,
      @JsonKey(name: 'created_at') DateTime createdAt,
      bool read,
      @JsonKey(name: 'pantry_item_id') String? pantryItemId,
      @JsonKey(name: 'dish_ids') List<String> dishIds});
}

/// @nodoc
class _$AppNotificationDtoCopyWithImpl<$Res>
    implements $AppNotificationDtoCopyWith<$Res> {
  _$AppNotificationDtoCopyWithImpl(this._self, this._then);

  final AppNotificationDto _self;
  final $Res Function(AppNotificationDto) _then;

  /// Create a copy of AppNotificationDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? type = null,
    Object? title = null,
    Object? body = null,
    Object? createdAt = null,
    Object? read = null,
    Object? pantryItemId = freezed,
    Object? dishIds = null,
  }) {
    return _then(_self.copyWith(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _self.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _self.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      body: null == body
          ? _self.body
          : body // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _self.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      read: null == read
          ? _self.read
          : read // ignore: cast_nullable_to_non_nullable
              as bool,
      pantryItemId: freezed == pantryItemId
          ? _self.pantryItemId
          : pantryItemId // ignore: cast_nullable_to_non_nullable
              as String?,
      dishIds: null == dishIds
          ? _self.dishIds
          : dishIds // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// Adds pattern-matching-related methods to [AppNotificationDto].
extension AppNotificationDtoPatterns on AppNotificationDto {
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
    TResult Function(_AppNotificationDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _AppNotificationDto() when $default != null:
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
    TResult Function(_AppNotificationDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _AppNotificationDto():
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
    TResult? Function(_AppNotificationDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _AppNotificationDto() when $default != null:
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
            String type,
            String title,
            String body,
            @JsonKey(name: 'created_at') DateTime createdAt,
            bool read,
            @JsonKey(name: 'pantry_item_id') String? pantryItemId,
            @JsonKey(name: 'dish_ids') List<String> dishIds)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _AppNotificationDto() when $default != null:
        return $default(_that.id, _that.type, _that.title, _that.body,
            _that.createdAt, _that.read, _that.pantryItemId, _that.dishIds);
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
            String type,
            String title,
            String body,
            @JsonKey(name: 'created_at') DateTime createdAt,
            bool read,
            @JsonKey(name: 'pantry_item_id') String? pantryItemId,
            @JsonKey(name: 'dish_ids') List<String> dishIds)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _AppNotificationDto():
        return $default(_that.id, _that.type, _that.title, _that.body,
            _that.createdAt, _that.read, _that.pantryItemId, _that.dishIds);
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
            String type,
            String title,
            String body,
            @JsonKey(name: 'created_at') DateTime createdAt,
            bool read,
            @JsonKey(name: 'pantry_item_id') String? pantryItemId,
            @JsonKey(name: 'dish_ids') List<String> dishIds)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _AppNotificationDto() when $default != null:
        return $default(_that.id, _that.type, _that.title, _that.body,
            _that.createdAt, _that.read, _that.pantryItemId, _that.dishIds);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _AppNotificationDto extends AppNotificationDto {
  const _AppNotificationDto(
      {required this.id,
      required this.type,
      required this.title,
      required this.body,
      @JsonKey(name: 'created_at') required this.createdAt,
      this.read = false,
      @JsonKey(name: 'pantry_item_id') this.pantryItemId,
      @JsonKey(name: 'dish_ids') final List<String> dishIds = const <String>[]})
      : _dishIds = dishIds,
        super._();
  factory _AppNotificationDto.fromJson(Map<String, dynamic> json) =>
      _$AppNotificationDtoFromJson(json);

  @override
  final String id;
  @override
  final String type;
  @override
  final String title;
  @override
  final String body;
  @override
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @override
  @JsonKey()
  final bool read;
  @override
  @JsonKey(name: 'pantry_item_id')
  final String? pantryItemId;
  final List<String> _dishIds;
  @override
  @JsonKey(name: 'dish_ids')
  List<String> get dishIds {
    if (_dishIds is EqualUnmodifiableListView) return _dishIds;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_dishIds);
  }

  /// Create a copy of AppNotificationDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$AppNotificationDtoCopyWith<_AppNotificationDto> get copyWith =>
      __$AppNotificationDtoCopyWithImpl<_AppNotificationDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$AppNotificationDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _AppNotificationDto &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.body, body) || other.body == body) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.read, read) || other.read == read) &&
            (identical(other.pantryItemId, pantryItemId) ||
                other.pantryItemId == pantryItemId) &&
            const DeepCollectionEquality().equals(other._dishIds, _dishIds));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, type, title, body, createdAt,
      read, pantryItemId, const DeepCollectionEquality().hash(_dishIds));

  @override
  String toString() {
    return 'AppNotificationDto(id: $id, type: $type, title: $title, body: $body, createdAt: $createdAt, read: $read, pantryItemId: $pantryItemId, dishIds: $dishIds)';
  }
}

/// @nodoc
abstract mixin class _$AppNotificationDtoCopyWith<$Res>
    implements $AppNotificationDtoCopyWith<$Res> {
  factory _$AppNotificationDtoCopyWith(
          _AppNotificationDto value, $Res Function(_AppNotificationDto) _then) =
      __$AppNotificationDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String id,
      String type,
      String title,
      String body,
      @JsonKey(name: 'created_at') DateTime createdAt,
      bool read,
      @JsonKey(name: 'pantry_item_id') String? pantryItemId,
      @JsonKey(name: 'dish_ids') List<String> dishIds});
}

/// @nodoc
class __$AppNotificationDtoCopyWithImpl<$Res>
    implements _$AppNotificationDtoCopyWith<$Res> {
  __$AppNotificationDtoCopyWithImpl(this._self, this._then);

  final _AppNotificationDto _self;
  final $Res Function(_AppNotificationDto) _then;

  /// Create a copy of AppNotificationDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? id = null,
    Object? type = null,
    Object? title = null,
    Object? body = null,
    Object? createdAt = null,
    Object? read = null,
    Object? pantryItemId = freezed,
    Object? dishIds = null,
  }) {
    return _then(_AppNotificationDto(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _self.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _self.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      body: null == body
          ? _self.body
          : body // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _self.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      read: null == read
          ? _self.read
          : read // ignore: cast_nullable_to_non_nullable
              as bool,
      pantryItemId: freezed == pantryItemId
          ? _self.pantryItemId
          : pantryItemId // ignore: cast_nullable_to_non_nullable
              as String?,
      dishIds: null == dishIds
          ? _self._dishIds
          : dishIds // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

// dart format on
