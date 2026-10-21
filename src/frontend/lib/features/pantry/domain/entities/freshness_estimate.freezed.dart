// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'freshness_estimate.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$FreshnessEstimate {

 Map<String, String> get answers; Map<String, String> get otherAnswers; DateTime get expiresAt; int? get remainingDaysMin; int? get remainingDaysMax; bool get blocked;
/// Create a copy of FreshnessEstimate
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FreshnessEstimateCopyWith<FreshnessEstimate> get copyWith => _$FreshnessEstimateCopyWithImpl<FreshnessEstimate>(this as FreshnessEstimate, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FreshnessEstimate&&const DeepCollectionEquality().equals(other.answers, answers)&&const DeepCollectionEquality().equals(other.otherAnswers, otherAnswers)&&(identical(other.expiresAt, expiresAt) || other.expiresAt == expiresAt)&&(identical(other.remainingDaysMin, remainingDaysMin) || other.remainingDaysMin == remainingDaysMin)&&(identical(other.remainingDaysMax, remainingDaysMax) || other.remainingDaysMax == remainingDaysMax)&&(identical(other.blocked, blocked) || other.blocked == blocked));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(answers),const DeepCollectionEquality().hash(otherAnswers),expiresAt,remainingDaysMin,remainingDaysMax,blocked);

@override
String toString() {
  return 'FreshnessEstimate(answers: $answers, otherAnswers: $otherAnswers, expiresAt: $expiresAt, remainingDaysMin: $remainingDaysMin, remainingDaysMax: $remainingDaysMax, blocked: $blocked)';
}


}

/// @nodoc
abstract mixin class $FreshnessEstimateCopyWith<$Res>  {
  factory $FreshnessEstimateCopyWith(FreshnessEstimate value, $Res Function(FreshnessEstimate) _then) = _$FreshnessEstimateCopyWithImpl;
@useResult
$Res call({
 Map<String, String> answers, Map<String, String> otherAnswers, DateTime expiresAt, int? remainingDaysMin, int? remainingDaysMax, bool blocked
});




}
/// @nodoc
class _$FreshnessEstimateCopyWithImpl<$Res>
    implements $FreshnessEstimateCopyWith<$Res> {
  _$FreshnessEstimateCopyWithImpl(this._self, this._then);

  final FreshnessEstimate _self;
  final $Res Function(FreshnessEstimate) _then;

/// Create a copy of FreshnessEstimate
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? answers = null,Object? otherAnswers = null,Object? expiresAt = null,Object? remainingDaysMin = freezed,Object? remainingDaysMax = freezed,Object? blocked = null,}) {
  return _then(_self.copyWith(
answers: null == answers ? _self.answers : answers // ignore: cast_nullable_to_non_nullable
as Map<String, String>,otherAnswers: null == otherAnswers ? _self.otherAnswers : otherAnswers // ignore: cast_nullable_to_non_nullable
as Map<String, String>,expiresAt: null == expiresAt ? _self.expiresAt : expiresAt // ignore: cast_nullable_to_non_nullable
as DateTime,remainingDaysMin: freezed == remainingDaysMin ? _self.remainingDaysMin : remainingDaysMin // ignore: cast_nullable_to_non_nullable
as int?,remainingDaysMax: freezed == remainingDaysMax ? _self.remainingDaysMax : remainingDaysMax // ignore: cast_nullable_to_non_nullable
as int?,blocked: null == blocked ? _self.blocked : blocked // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [FreshnessEstimate].
extension FreshnessEstimatePatterns on FreshnessEstimate {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FreshnessEstimate value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FreshnessEstimate() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FreshnessEstimate value)  $default,){
final _that = this;
switch (_that) {
case _FreshnessEstimate():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FreshnessEstimate value)?  $default,){
final _that = this;
switch (_that) {
case _FreshnessEstimate() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( Map<String, String> answers,  Map<String, String> otherAnswers,  DateTime expiresAt,  int? remainingDaysMin,  int? remainingDaysMax,  bool blocked)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FreshnessEstimate() when $default != null:
return $default(_that.answers,_that.otherAnswers,_that.expiresAt,_that.remainingDaysMin,_that.remainingDaysMax,_that.blocked);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( Map<String, String> answers,  Map<String, String> otherAnswers,  DateTime expiresAt,  int? remainingDaysMin,  int? remainingDaysMax,  bool blocked)  $default,) {final _that = this;
switch (_that) {
case _FreshnessEstimate():
return $default(_that.answers,_that.otherAnswers,_that.expiresAt,_that.remainingDaysMin,_that.remainingDaysMax,_that.blocked);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( Map<String, String> answers,  Map<String, String> otherAnswers,  DateTime expiresAt,  int? remainingDaysMin,  int? remainingDaysMax,  bool blocked)?  $default,) {final _that = this;
switch (_that) {
case _FreshnessEstimate() when $default != null:
return $default(_that.answers,_that.otherAnswers,_that.expiresAt,_that.remainingDaysMin,_that.remainingDaysMax,_that.blocked);case _:
  return null;

}
}

}

/// @nodoc


class _FreshnessEstimate implements FreshnessEstimate {
  const _FreshnessEstimate({required final  Map<String, String> answers, final  Map<String, String> otherAnswers = const <String, String>{}, required this.expiresAt, this.remainingDaysMin, this.remainingDaysMax, this.blocked = false}): _answers = answers,_otherAnswers = otherAnswers;
  

 final  Map<String, String> _answers;
@override Map<String, String> get answers {
  if (_answers is EqualUnmodifiableMapView) return _answers;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_answers);
}

 final  Map<String, String> _otherAnswers;
@override@JsonKey() Map<String, String> get otherAnswers {
  if (_otherAnswers is EqualUnmodifiableMapView) return _otherAnswers;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_otherAnswers);
}

@override final  DateTime expiresAt;
@override final  int? remainingDaysMin;
@override final  int? remainingDaysMax;
@override@JsonKey() final  bool blocked;

/// Create a copy of FreshnessEstimate
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FreshnessEstimateCopyWith<_FreshnessEstimate> get copyWith => __$FreshnessEstimateCopyWithImpl<_FreshnessEstimate>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FreshnessEstimate&&const DeepCollectionEquality().equals(other._answers, _answers)&&const DeepCollectionEquality().equals(other._otherAnswers, _otherAnswers)&&(identical(other.expiresAt, expiresAt) || other.expiresAt == expiresAt)&&(identical(other.remainingDaysMin, remainingDaysMin) || other.remainingDaysMin == remainingDaysMin)&&(identical(other.remainingDaysMax, remainingDaysMax) || other.remainingDaysMax == remainingDaysMax)&&(identical(other.blocked, blocked) || other.blocked == blocked));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_answers),const DeepCollectionEquality().hash(_otherAnswers),expiresAt,remainingDaysMin,remainingDaysMax,blocked);

@override
String toString() {
  return 'FreshnessEstimate(answers: $answers, otherAnswers: $otherAnswers, expiresAt: $expiresAt, remainingDaysMin: $remainingDaysMin, remainingDaysMax: $remainingDaysMax, blocked: $blocked)';
}


}

/// @nodoc
abstract mixin class _$FreshnessEstimateCopyWith<$Res> implements $FreshnessEstimateCopyWith<$Res> {
  factory _$FreshnessEstimateCopyWith(_FreshnessEstimate value, $Res Function(_FreshnessEstimate) _then) = __$FreshnessEstimateCopyWithImpl;
@override @useResult
$Res call({
 Map<String, String> answers, Map<String, String> otherAnswers, DateTime expiresAt, int? remainingDaysMin, int? remainingDaysMax, bool blocked
});




}
/// @nodoc
class __$FreshnessEstimateCopyWithImpl<$Res>
    implements _$FreshnessEstimateCopyWith<$Res> {
  __$FreshnessEstimateCopyWithImpl(this._self, this._then);

  final _FreshnessEstimate _self;
  final $Res Function(_FreshnessEstimate) _then;

/// Create a copy of FreshnessEstimate
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? answers = null,Object? otherAnswers = null,Object? expiresAt = null,Object? remainingDaysMin = freezed,Object? remainingDaysMax = freezed,Object? blocked = null,}) {
  return _then(_FreshnessEstimate(
answers: null == answers ? _self._answers : answers // ignore: cast_nullable_to_non_nullable
as Map<String, String>,otherAnswers: null == otherAnswers ? _self._otherAnswers : otherAnswers // ignore: cast_nullable_to_non_nullable
as Map<String, String>,expiresAt: null == expiresAt ? _self.expiresAt : expiresAt // ignore: cast_nullable_to_non_nullable
as DateTime,remainingDaysMin: freezed == remainingDaysMin ? _self.remainingDaysMin : remainingDaysMin // ignore: cast_nullable_to_non_nullable
as int?,remainingDaysMax: freezed == remainingDaysMax ? _self.remainingDaysMax : remainingDaysMax // ignore: cast_nullable_to_non_nullable
as int?,blocked: null == blocked ? _self.blocked : blocked // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
