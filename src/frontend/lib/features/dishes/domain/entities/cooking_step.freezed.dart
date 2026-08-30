// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'cooking_step.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$CookingStep {
  int get order;
  String get text;
  int? get durationMin;

  /// Create a copy of CookingStep
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $CookingStepCopyWith<CookingStep> get copyWith =>
      _$CookingStepCopyWithImpl<CookingStep>(this as CookingStep, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is CookingStep &&
            (identical(other.order, order) || other.order == order) &&
            (identical(other.text, text) || other.text == text) &&
            (identical(other.durationMin, durationMin) ||
                other.durationMin == durationMin));
  }

  @override
  int get hashCode => Object.hash(runtimeType, order, text, durationMin);

  @override
  String toString() {
    return 'CookingStep(order: $order, text: $text, durationMin: $durationMin)';
  }
}

/// @nodoc
abstract mixin class $CookingStepCopyWith<$Res> {
  factory $CookingStepCopyWith(
          CookingStep value, $Res Function(CookingStep) _then) =
      _$CookingStepCopyWithImpl;
  @useResult
  $Res call({int order, String text, int? durationMin});
}

/// @nodoc
class _$CookingStepCopyWithImpl<$Res> implements $CookingStepCopyWith<$Res> {
  _$CookingStepCopyWithImpl(this._self, this._then);

  final CookingStep _self;
  final $Res Function(CookingStep) _then;

  /// Create a copy of CookingStep
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? order = null,
    Object? text = null,
    Object? durationMin = freezed,
  }) {
    return _then(_self.copyWith(
      order: null == order
          ? _self.order
          : order // ignore: cast_nullable_to_non_nullable
              as int,
      text: null == text
          ? _self.text
          : text // ignore: cast_nullable_to_non_nullable
              as String,
      durationMin: freezed == durationMin
          ? _self.durationMin
          : durationMin // ignore: cast_nullable_to_non_nullable
              as int?,
    ));
  }
}

/// Adds pattern-matching-related methods to [CookingStep].
extension CookingStepPatterns on CookingStep {
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
    TResult Function(_CookingStep value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _CookingStep() when $default != null:
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
    TResult Function(_CookingStep value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookingStep():
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
    TResult? Function(_CookingStep value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookingStep() when $default != null:
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
    TResult Function(int order, String text, int? durationMin)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _CookingStep() when $default != null:
        return $default(_that.order, _that.text, _that.durationMin);
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
    TResult Function(int order, String text, int? durationMin) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookingStep():
        return $default(_that.order, _that.text, _that.durationMin);
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
    TResult? Function(int order, String text, int? durationMin)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookingStep() when $default != null:
        return $default(_that.order, _that.text, _that.durationMin);
      case _:
        return null;
    }
  }
}

/// @nodoc

class _CookingStep extends CookingStep {
  const _CookingStep(
      {required this.order, required this.text, this.durationMin})
      : super._();

  @override
  final int order;
  @override
  final String text;
  @override
  final int? durationMin;

  /// Create a copy of CookingStep
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$CookingStepCopyWith<_CookingStep> get copyWith =>
      __$CookingStepCopyWithImpl<_CookingStep>(this, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _CookingStep &&
            (identical(other.order, order) || other.order == order) &&
            (identical(other.text, text) || other.text == text) &&
            (identical(other.durationMin, durationMin) ||
                other.durationMin == durationMin));
  }

  @override
  int get hashCode => Object.hash(runtimeType, order, text, durationMin);

  @override
  String toString() {
    return 'CookingStep(order: $order, text: $text, durationMin: $durationMin)';
  }
}

/// @nodoc
abstract mixin class _$CookingStepCopyWith<$Res>
    implements $CookingStepCopyWith<$Res> {
  factory _$CookingStepCopyWith(
          _CookingStep value, $Res Function(_CookingStep) _then) =
      __$CookingStepCopyWithImpl;
  @override
  @useResult
  $Res call({int order, String text, int? durationMin});
}

/// @nodoc
class __$CookingStepCopyWithImpl<$Res> implements _$CookingStepCopyWith<$Res> {
  __$CookingStepCopyWithImpl(this._self, this._then);

  final _CookingStep _self;
  final $Res Function(_CookingStep) _then;

  /// Create a copy of CookingStep
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? order = null,
    Object? text = null,
    Object? durationMin = freezed,
  }) {
    return _then(_CookingStep(
      order: null == order
          ? _self.order
          : order // ignore: cast_nullable_to_non_nullable
              as int,
      text: null == text
          ? _self.text
          : text // ignore: cast_nullable_to_non_nullable
              as String,
      durationMin: freezed == durationMin
          ? _self.durationMin
          : durationMin // ignore: cast_nullable_to_non_nullable
              as int?,
    ));
  }
}

// dart format on
