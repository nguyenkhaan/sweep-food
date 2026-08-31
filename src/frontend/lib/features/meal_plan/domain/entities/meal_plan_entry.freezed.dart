// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'meal_plan_entry.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$MealPlanEntry {
  DateTime get date;
  MealSlot get slot;
  String get dishId;
  String? get dishName;
  String? get dishImageUrl;

  /// Create a copy of MealPlanEntry
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $MealPlanEntryCopyWith<MealPlanEntry> get copyWith =>
      _$MealPlanEntryCopyWithImpl<MealPlanEntry>(
          this as MealPlanEntry, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is MealPlanEntry &&
            (identical(other.date, date) || other.date == date) &&
            (identical(other.slot, slot) || other.slot == slot) &&
            (identical(other.dishId, dishId) || other.dishId == dishId) &&
            (identical(other.dishName, dishName) ||
                other.dishName == dishName) &&
            (identical(other.dishImageUrl, dishImageUrl) ||
                other.dishImageUrl == dishImageUrl));
  }

  @override
  int get hashCode =>
      Object.hash(runtimeType, date, slot, dishId, dishName, dishImageUrl);

  @override
  String toString() {
    return 'MealPlanEntry(date: $date, slot: $slot, dishId: $dishId, dishName: $dishName, dishImageUrl: $dishImageUrl)';
  }
}

/// @nodoc
abstract mixin class $MealPlanEntryCopyWith<$Res> {
  factory $MealPlanEntryCopyWith(
          MealPlanEntry value, $Res Function(MealPlanEntry) _then) =
      _$MealPlanEntryCopyWithImpl;
  @useResult
  $Res call(
      {DateTime date,
      MealSlot slot,
      String dishId,
      String? dishName,
      String? dishImageUrl});
}

/// @nodoc
class _$MealPlanEntryCopyWithImpl<$Res>
    implements $MealPlanEntryCopyWith<$Res> {
  _$MealPlanEntryCopyWithImpl(this._self, this._then);

  final MealPlanEntry _self;
  final $Res Function(MealPlanEntry) _then;

  /// Create a copy of MealPlanEntry
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? date = null,
    Object? slot = null,
    Object? dishId = null,
    Object? dishName = freezed,
    Object? dishImageUrl = freezed,
  }) {
    return _then(_self.copyWith(
      date: null == date
          ? _self.date
          : date // ignore: cast_nullable_to_non_nullable
              as DateTime,
      slot: null == slot
          ? _self.slot
          : slot // ignore: cast_nullable_to_non_nullable
              as MealSlot,
      dishId: null == dishId
          ? _self.dishId
          : dishId // ignore: cast_nullable_to_non_nullable
              as String,
      dishName: freezed == dishName
          ? _self.dishName
          : dishName // ignore: cast_nullable_to_non_nullable
              as String?,
      dishImageUrl: freezed == dishImageUrl
          ? _self.dishImageUrl
          : dishImageUrl // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// Adds pattern-matching-related methods to [MealPlanEntry].
extension MealPlanEntryPatterns on MealPlanEntry {
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
    TResult Function(_MealPlanEntry value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _MealPlanEntry() when $default != null:
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
    TResult Function(_MealPlanEntry value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _MealPlanEntry():
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
    TResult? Function(_MealPlanEntry value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _MealPlanEntry() when $default != null:
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
    TResult Function(DateTime date, MealSlot slot, String dishId,
            String? dishName, String? dishImageUrl)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _MealPlanEntry() when $default != null:
        return $default(_that.date, _that.slot, _that.dishId, _that.dishName,
            _that.dishImageUrl);
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
    TResult Function(DateTime date, MealSlot slot, String dishId,
            String? dishName, String? dishImageUrl)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _MealPlanEntry():
        return $default(_that.date, _that.slot, _that.dishId, _that.dishName,
            _that.dishImageUrl);
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
    TResult? Function(DateTime date, MealSlot slot, String dishId,
            String? dishName, String? dishImageUrl)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _MealPlanEntry() when $default != null:
        return $default(_that.date, _that.slot, _that.dishId, _that.dishName,
            _that.dishImageUrl);
      case _:
        return null;
    }
  }
}

/// @nodoc

class _MealPlanEntry extends MealPlanEntry {
  const _MealPlanEntry(
      {required this.date,
      required this.slot,
      required this.dishId,
      this.dishName,
      this.dishImageUrl})
      : super._();

  @override
  final DateTime date;
  @override
  final MealSlot slot;
  @override
  final String dishId;
  @override
  final String? dishName;
  @override
  final String? dishImageUrl;

  /// Create a copy of MealPlanEntry
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$MealPlanEntryCopyWith<_MealPlanEntry> get copyWith =>
      __$MealPlanEntryCopyWithImpl<_MealPlanEntry>(this, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _MealPlanEntry &&
            (identical(other.date, date) || other.date == date) &&
            (identical(other.slot, slot) || other.slot == slot) &&
            (identical(other.dishId, dishId) || other.dishId == dishId) &&
            (identical(other.dishName, dishName) ||
                other.dishName == dishName) &&
            (identical(other.dishImageUrl, dishImageUrl) ||
                other.dishImageUrl == dishImageUrl));
  }

  @override
  int get hashCode =>
      Object.hash(runtimeType, date, slot, dishId, dishName, dishImageUrl);

  @override
  String toString() {
    return 'MealPlanEntry(date: $date, slot: $slot, dishId: $dishId, dishName: $dishName, dishImageUrl: $dishImageUrl)';
  }
}

/// @nodoc
abstract mixin class _$MealPlanEntryCopyWith<$Res>
    implements $MealPlanEntryCopyWith<$Res> {
  factory _$MealPlanEntryCopyWith(
          _MealPlanEntry value, $Res Function(_MealPlanEntry) _then) =
      __$MealPlanEntryCopyWithImpl;
  @override
  @useResult
  $Res call(
      {DateTime date,
      MealSlot slot,
      String dishId,
      String? dishName,
      String? dishImageUrl});
}

/// @nodoc
class __$MealPlanEntryCopyWithImpl<$Res>
    implements _$MealPlanEntryCopyWith<$Res> {
  __$MealPlanEntryCopyWithImpl(this._self, this._then);

  final _MealPlanEntry _self;
  final $Res Function(_MealPlanEntry) _then;

  /// Create a copy of MealPlanEntry
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? date = null,
    Object? slot = null,
    Object? dishId = null,
    Object? dishName = freezed,
    Object? dishImageUrl = freezed,
  }) {
    return _then(_MealPlanEntry(
      date: null == date
          ? _self.date
          : date // ignore: cast_nullable_to_non_nullable
              as DateTime,
      slot: null == slot
          ? _self.slot
          : slot // ignore: cast_nullable_to_non_nullable
              as MealSlot,
      dishId: null == dishId
          ? _self.dishId
          : dishId // ignore: cast_nullable_to_non_nullable
              as String,
      dishName: freezed == dishName
          ? _self.dishName
          : dishName // ignore: cast_nullable_to_non_nullable
              as String?,
      dishImageUrl: freezed == dishImageUrl
          ? _self.dishImageUrl
          : dishImageUrl // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

// dart format on
