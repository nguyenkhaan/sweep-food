// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'app_notification.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$AppNotification {
  String get id;
  AppNotificationType get type;
  String get title;
  String get body;
  DateTime get createdAt;
  bool get read;

  /// Deep-link targets (set by type). `pantryItemId` for near-expiry,
  /// `dishIds` for "xem món gợi ý".
  String? get pantryItemId;
  List<String> get dishIds;

  /// Create a copy of AppNotification
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $AppNotificationCopyWith<AppNotification> get copyWith =>
      _$AppNotificationCopyWithImpl<AppNotification>(
          this as AppNotification, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is AppNotification &&
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

  @override
  int get hashCode => Object.hash(runtimeType, id, type, title, body, createdAt,
      read, pantryItemId, const DeepCollectionEquality().hash(dishIds));

  @override
  String toString() {
    return 'AppNotification(id: $id, type: $type, title: $title, body: $body, createdAt: $createdAt, read: $read, pantryItemId: $pantryItemId, dishIds: $dishIds)';
  }
}

/// @nodoc
abstract mixin class $AppNotificationCopyWith<$Res> {
  factory $AppNotificationCopyWith(
          AppNotification value, $Res Function(AppNotification) _then) =
      _$AppNotificationCopyWithImpl;
  @useResult
  $Res call(
      {String id,
      AppNotificationType type,
      String title,
      String body,
      DateTime createdAt,
      bool read,
      String? pantryItemId,
      List<String> dishIds});
}

/// @nodoc
class _$AppNotificationCopyWithImpl<$Res>
    implements $AppNotificationCopyWith<$Res> {
  _$AppNotificationCopyWithImpl(this._self, this._then);

  final AppNotification _self;
  final $Res Function(AppNotification) _then;

  /// Create a copy of AppNotification
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
              as AppNotificationType,
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

/// Adds pattern-matching-related methods to [AppNotification].
extension AppNotificationPatterns on AppNotification {
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
    TResult Function(_AppNotification value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _AppNotification() when $default != null:
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
    TResult Function(_AppNotification value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _AppNotification():
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
    TResult? Function(_AppNotification value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _AppNotification() when $default != null:
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
            AppNotificationType type,
            String title,
            String body,
            DateTime createdAt,
            bool read,
            String? pantryItemId,
            List<String> dishIds)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _AppNotification() when $default != null:
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
            AppNotificationType type,
            String title,
            String body,
            DateTime createdAt,
            bool read,
            String? pantryItemId,
            List<String> dishIds)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _AppNotification():
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
            AppNotificationType type,
            String title,
            String body,
            DateTime createdAt,
            bool read,
            String? pantryItemId,
            List<String> dishIds)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _AppNotification() when $default != null:
        return $default(_that.id, _that.type, _that.title, _that.body,
            _that.createdAt, _that.read, _that.pantryItemId, _that.dishIds);
      case _:
        return null;
    }
  }
}

/// @nodoc

class _AppNotification extends AppNotification {
  const _AppNotification(
      {required this.id,
      required this.type,
      required this.title,
      required this.body,
      required this.createdAt,
      this.read = false,
      this.pantryItemId,
      final List<String> dishIds = const []})
      : _dishIds = dishIds,
        super._();

  @override
  final String id;
  @override
  final AppNotificationType type;
  @override
  final String title;
  @override
  final String body;
  @override
  final DateTime createdAt;
  @override
  @JsonKey()
  final bool read;

  /// Deep-link targets (set by type). `pantryItemId` for near-expiry,
  /// `dishIds` for "xem món gợi ý".
  @override
  final String? pantryItemId;
  final List<String> _dishIds;
  @override
  @JsonKey()
  List<String> get dishIds {
    if (_dishIds is EqualUnmodifiableListView) return _dishIds;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_dishIds);
  }

  /// Create a copy of AppNotification
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$AppNotificationCopyWith<_AppNotification> get copyWith =>
      __$AppNotificationCopyWithImpl<_AppNotification>(this, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _AppNotification &&
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

  @override
  int get hashCode => Object.hash(runtimeType, id, type, title, body, createdAt,
      read, pantryItemId, const DeepCollectionEquality().hash(_dishIds));

  @override
  String toString() {
    return 'AppNotification(id: $id, type: $type, title: $title, body: $body, createdAt: $createdAt, read: $read, pantryItemId: $pantryItemId, dishIds: $dishIds)';
  }
}

/// @nodoc
abstract mixin class _$AppNotificationCopyWith<$Res>
    implements $AppNotificationCopyWith<$Res> {
  factory _$AppNotificationCopyWith(
          _AppNotification value, $Res Function(_AppNotification) _then) =
      __$AppNotificationCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String id,
      AppNotificationType type,
      String title,
      String body,
      DateTime createdAt,
      bool read,
      String? pantryItemId,
      List<String> dishIds});
}

/// @nodoc
class __$AppNotificationCopyWithImpl<$Res>
    implements _$AppNotificationCopyWith<$Res> {
  __$AppNotificationCopyWithImpl(this._self, this._then);

  final _AppNotification _self;
  final $Res Function(_AppNotification) _then;

  /// Create a copy of AppNotification
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
    return _then(_AppNotification(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _self.type
          : type // ignore: cast_nullable_to_non_nullable
              as AppNotificationType,
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
