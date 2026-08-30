// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'score_breakdown.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ScoreBreakdown {
  /// E — how much near-expiry stock the dish uses up.
  double get e;

  /// A — share of ingredients already in the pantry.
  double get a;

  /// P — fit with servings, nutrition target and preferences.
  double get p;

  /// U — how little extra shopping it needs.
  double get u;

  /// Create a copy of ScoreBreakdown
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $ScoreBreakdownCopyWith<ScoreBreakdown> get copyWith =>
      _$ScoreBreakdownCopyWithImpl<ScoreBreakdown>(
          this as ScoreBreakdown, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is ScoreBreakdown &&
            (identical(other.e, e) || other.e == e) &&
            (identical(other.a, a) || other.a == a) &&
            (identical(other.p, p) || other.p == p) &&
            (identical(other.u, u) || other.u == u));
  }

  @override
  int get hashCode => Object.hash(runtimeType, e, a, p, u);

  @override
  String toString() {
    return 'ScoreBreakdown(e: $e, a: $a, p: $p, u: $u)';
  }
}

/// @nodoc
abstract mixin class $ScoreBreakdownCopyWith<$Res> {
  factory $ScoreBreakdownCopyWith(
          ScoreBreakdown value, $Res Function(ScoreBreakdown) _then) =
      _$ScoreBreakdownCopyWithImpl;
  @useResult
  $Res call({double e, double a, double p, double u});
}

/// @nodoc
class _$ScoreBreakdownCopyWithImpl<$Res>
    implements $ScoreBreakdownCopyWith<$Res> {
  _$ScoreBreakdownCopyWithImpl(this._self, this._then);

  final ScoreBreakdown _self;
  final $Res Function(ScoreBreakdown) _then;

  /// Create a copy of ScoreBreakdown
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? e = null,
    Object? a = null,
    Object? p = null,
    Object? u = null,
  }) {
    return _then(_self.copyWith(
      e: null == e
          ? _self.e
          : e // ignore: cast_nullable_to_non_nullable
              as double,
      a: null == a
          ? _self.a
          : a // ignore: cast_nullable_to_non_nullable
              as double,
      p: null == p
          ? _self.p
          : p // ignore: cast_nullable_to_non_nullable
              as double,
      u: null == u
          ? _self.u
          : u // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// Adds pattern-matching-related methods to [ScoreBreakdown].
extension ScoreBreakdownPatterns on ScoreBreakdown {
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
    TResult Function(_ScoreBreakdown value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _ScoreBreakdown() when $default != null:
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
    TResult Function(_ScoreBreakdown value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _ScoreBreakdown():
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
    TResult? Function(_ScoreBreakdown value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _ScoreBreakdown() when $default != null:
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
    TResult Function(double e, double a, double p, double u)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _ScoreBreakdown() when $default != null:
        return $default(_that.e, _that.a, _that.p, _that.u);
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
    TResult Function(double e, double a, double p, double u) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _ScoreBreakdown():
        return $default(_that.e, _that.a, _that.p, _that.u);
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
    TResult? Function(double e, double a, double p, double u)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _ScoreBreakdown() when $default != null:
        return $default(_that.e, _that.a, _that.p, _that.u);
      case _:
        return null;
    }
  }
}

/// @nodoc

class _ScoreBreakdown extends ScoreBreakdown {
  const _ScoreBreakdown({this.e = 0, this.a = 0, this.p = 0, this.u = 0})
      : super._();

  /// E — how much near-expiry stock the dish uses up.
  @override
  @JsonKey()
  final double e;

  /// A — share of ingredients already in the pantry.
  @override
  @JsonKey()
  final double a;

  /// P — fit with servings, nutrition target and preferences.
  @override
  @JsonKey()
  final double p;

  /// U — how little extra shopping it needs.
  @override
  @JsonKey()
  final double u;

  /// Create a copy of ScoreBreakdown
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$ScoreBreakdownCopyWith<_ScoreBreakdown> get copyWith =>
      __$ScoreBreakdownCopyWithImpl<_ScoreBreakdown>(this, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _ScoreBreakdown &&
            (identical(other.e, e) || other.e == e) &&
            (identical(other.a, a) || other.a == a) &&
            (identical(other.p, p) || other.p == p) &&
            (identical(other.u, u) || other.u == u));
  }

  @override
  int get hashCode => Object.hash(runtimeType, e, a, p, u);

  @override
  String toString() {
    return 'ScoreBreakdown(e: $e, a: $a, p: $p, u: $u)';
  }
}

/// @nodoc
abstract mixin class _$ScoreBreakdownCopyWith<$Res>
    implements $ScoreBreakdownCopyWith<$Res> {
  factory _$ScoreBreakdownCopyWith(
          _ScoreBreakdown value, $Res Function(_ScoreBreakdown) _then) =
      __$ScoreBreakdownCopyWithImpl;
  @override
  @useResult
  $Res call({double e, double a, double p, double u});
}

/// @nodoc
class __$ScoreBreakdownCopyWithImpl<$Res>
    implements _$ScoreBreakdownCopyWith<$Res> {
  __$ScoreBreakdownCopyWithImpl(this._self, this._then);

  final _ScoreBreakdown _self;
  final $Res Function(_ScoreBreakdown) _then;

  /// Create a copy of ScoreBreakdown
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? e = null,
    Object? a = null,
    Object? p = null,
    Object? u = null,
  }) {
    return _then(_ScoreBreakdown(
      e: null == e
          ? _self.e
          : e // ignore: cast_nullable_to_non_nullable
              as double,
      a: null == a
          ? _self.a
          : a // ignore: cast_nullable_to_non_nullable
              as double,
      p: null == p
          ? _self.p
          : p // ignore: cast_nullable_to_non_nullable
              as double,
      u: null == u
          ? _self.u
          : u // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

// dart format on
