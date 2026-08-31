// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'subscription.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Subscription {
  SubscriptionTier get tier;
  List<String> get perks;

  /// Whether this device has already registered premium interest (G-05).
  bool get premiumInterestRegistered;

  /// Create a copy of Subscription
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $SubscriptionCopyWith<Subscription> get copyWith =>
      _$SubscriptionCopyWithImpl<Subscription>(
          this as Subscription, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is Subscription &&
            (identical(other.tier, tier) || other.tier == tier) &&
            const DeepCollectionEquality().equals(other.perks, perks) &&
            (identical(other.premiumInterestRegistered,
                    premiumInterestRegistered) ||
                other.premiumInterestRegistered == premiumInterestRegistered));
  }

  @override
  int get hashCode => Object.hash(runtimeType, tier,
      const DeepCollectionEquality().hash(perks), premiumInterestRegistered);

  @override
  String toString() {
    return 'Subscription(tier: $tier, perks: $perks, premiumInterestRegistered: $premiumInterestRegistered)';
  }
}

/// @nodoc
abstract mixin class $SubscriptionCopyWith<$Res> {
  factory $SubscriptionCopyWith(
          Subscription value, $Res Function(Subscription) _then) =
      _$SubscriptionCopyWithImpl;
  @useResult
  $Res call(
      {SubscriptionTier tier,
      List<String> perks,
      bool premiumInterestRegistered});
}

/// @nodoc
class _$SubscriptionCopyWithImpl<$Res> implements $SubscriptionCopyWith<$Res> {
  _$SubscriptionCopyWithImpl(this._self, this._then);

  final Subscription _self;
  final $Res Function(Subscription) _then;

  /// Create a copy of Subscription
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? tier = null,
    Object? perks = null,
    Object? premiumInterestRegistered = null,
  }) {
    return _then(_self.copyWith(
      tier: null == tier
          ? _self.tier
          : tier // ignore: cast_nullable_to_non_nullable
              as SubscriptionTier,
      perks: null == perks
          ? _self.perks
          : perks // ignore: cast_nullable_to_non_nullable
              as List<String>,
      premiumInterestRegistered: null == premiumInterestRegistered
          ? _self.premiumInterestRegistered
          : premiumInterestRegistered // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// Adds pattern-matching-related methods to [Subscription].
extension SubscriptionPatterns on Subscription {
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
    TResult Function(_Subscription value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _Subscription() when $default != null:
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
    TResult Function(_Subscription value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Subscription():
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
    TResult? Function(_Subscription value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Subscription() when $default != null:
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
    TResult Function(SubscriptionTier tier, List<String> perks,
            bool premiumInterestRegistered)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _Subscription() when $default != null:
        return $default(
            _that.tier, _that.perks, _that.premiumInterestRegistered);
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
    TResult Function(SubscriptionTier tier, List<String> perks,
            bool premiumInterestRegistered)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Subscription():
        return $default(
            _that.tier, _that.perks, _that.premiumInterestRegistered);
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
    TResult? Function(SubscriptionTier tier, List<String> perks,
            bool premiumInterestRegistered)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Subscription() when $default != null:
        return $default(
            _that.tier, _that.perks, _that.premiumInterestRegistered);
      case _:
        return null;
    }
  }
}

/// @nodoc

class _Subscription extends Subscription {
  const _Subscription(
      {required this.tier,
      final List<String> perks = const <String>[],
      this.premiumInterestRegistered = false})
      : _perks = perks,
        super._();

  @override
  final SubscriptionTier tier;
  final List<String> _perks;
  @override
  @JsonKey()
  List<String> get perks {
    if (_perks is EqualUnmodifiableListView) return _perks;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_perks);
  }

  /// Whether this device has already registered premium interest (G-05).
  @override
  @JsonKey()
  final bool premiumInterestRegistered;

  /// Create a copy of Subscription
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$SubscriptionCopyWith<_Subscription> get copyWith =>
      __$SubscriptionCopyWithImpl<_Subscription>(this, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _Subscription &&
            (identical(other.tier, tier) || other.tier == tier) &&
            const DeepCollectionEquality().equals(other._perks, _perks) &&
            (identical(other.premiumInterestRegistered,
                    premiumInterestRegistered) ||
                other.premiumInterestRegistered == premiumInterestRegistered));
  }

  @override
  int get hashCode => Object.hash(runtimeType, tier,
      const DeepCollectionEquality().hash(_perks), premiumInterestRegistered);

  @override
  String toString() {
    return 'Subscription(tier: $tier, perks: $perks, premiumInterestRegistered: $premiumInterestRegistered)';
  }
}

/// @nodoc
abstract mixin class _$SubscriptionCopyWith<$Res>
    implements $SubscriptionCopyWith<$Res> {
  factory _$SubscriptionCopyWith(
          _Subscription value, $Res Function(_Subscription) _then) =
      __$SubscriptionCopyWithImpl;
  @override
  @useResult
  $Res call(
      {SubscriptionTier tier,
      List<String> perks,
      bool premiumInterestRegistered});
}

/// @nodoc
class __$SubscriptionCopyWithImpl<$Res>
    implements _$SubscriptionCopyWith<$Res> {
  __$SubscriptionCopyWithImpl(this._self, this._then);

  final _Subscription _self;
  final $Res Function(_Subscription) _then;

  /// Create a copy of Subscription
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? tier = null,
    Object? perks = null,
    Object? premiumInterestRegistered = null,
  }) {
    return _then(_Subscription(
      tier: null == tier
          ? _self.tier
          : tier // ignore: cast_nullable_to_non_nullable
              as SubscriptionTier,
      perks: null == perks
          ? _self._perks
          : perks // ignore: cast_nullable_to_non_nullable
              as List<String>,
      premiumInterestRegistered: null == premiumInterestRegistered
          ? _self.premiumInterestRegistered
          : premiumInterestRegistered // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

// dart format on
