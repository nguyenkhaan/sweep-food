// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'dish_suggestion.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$DishSuggestion {

 Dish get dish; ScoreBreakdown get breakdown;/// Names of near-expiry pantry ingredients this dish would use.
 List<String> get nearExpiryIngredients;/// Share of the dish's ingredients already in the pantry (`0..1`).
 double get availabilityRatio;/// How many ingredients still need buying.
 int get toBuyCount;/// Server-provided score override; falls back to [breakdown.scoreOutOf100].
 int? get scoreOverride;/// Human-readable explanation from recommendation engine / mock provider.
 String? get explanation;/// True if the score and ranking are from a mock provider (`analysis.is_mock`).
 bool get isMock;
/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DishSuggestionCopyWith<DishSuggestion> get copyWith => _$DishSuggestionCopyWithImpl<DishSuggestion>(this as DishSuggestion, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DishSuggestion&&(identical(other.dish, dish) || other.dish == dish)&&(identical(other.breakdown, breakdown) || other.breakdown == breakdown)&&const DeepCollectionEquality().equals(other.nearExpiryIngredients, nearExpiryIngredients)&&(identical(other.availabilityRatio, availabilityRatio) || other.availabilityRatio == availabilityRatio)&&(identical(other.toBuyCount, toBuyCount) || other.toBuyCount == toBuyCount)&&(identical(other.scoreOverride, scoreOverride) || other.scoreOverride == scoreOverride)&&(identical(other.explanation, explanation) || other.explanation == explanation)&&(identical(other.isMock, isMock) || other.isMock == isMock));
}


@override
int get hashCode => Object.hash(runtimeType,dish,breakdown,const DeepCollectionEquality().hash(nearExpiryIngredients),availabilityRatio,toBuyCount,scoreOverride,explanation,isMock);

@override
String toString() {
  return 'DishSuggestion(dish: $dish, breakdown: $breakdown, nearExpiryIngredients: $nearExpiryIngredients, availabilityRatio: $availabilityRatio, toBuyCount: $toBuyCount, scoreOverride: $scoreOverride, explanation: $explanation, isMock: $isMock)';
}


}

/// @nodoc
abstract mixin class $DishSuggestionCopyWith<$Res>  {
  factory $DishSuggestionCopyWith(DishSuggestion value, $Res Function(DishSuggestion) _then) = _$DishSuggestionCopyWithImpl;
@useResult
$Res call({
 Dish dish, ScoreBreakdown breakdown, List<String> nearExpiryIngredients, double availabilityRatio, int toBuyCount, int? scoreOverride, String? explanation, bool isMock
});


$DishCopyWith<$Res> get dish;$ScoreBreakdownCopyWith<$Res> get breakdown;

}
/// @nodoc
class _$DishSuggestionCopyWithImpl<$Res>
    implements $DishSuggestionCopyWith<$Res> {
  _$DishSuggestionCopyWithImpl(this._self, this._then);

  final DishSuggestion _self;
  final $Res Function(DishSuggestion) _then;

/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? dish = null,Object? breakdown = null,Object? nearExpiryIngredients = null,Object? availabilityRatio = null,Object? toBuyCount = null,Object? scoreOverride = freezed,Object? explanation = freezed,Object? isMock = null,}) {
  return _then(_self.copyWith(
dish: null == dish ? _self.dish : dish // ignore: cast_nullable_to_non_nullable
as Dish,breakdown: null == breakdown ? _self.breakdown : breakdown // ignore: cast_nullable_to_non_nullable
as ScoreBreakdown,nearExpiryIngredients: null == nearExpiryIngredients ? _self.nearExpiryIngredients : nearExpiryIngredients // ignore: cast_nullable_to_non_nullable
as List<String>,availabilityRatio: null == availabilityRatio ? _self.availabilityRatio : availabilityRatio // ignore: cast_nullable_to_non_nullable
as double,toBuyCount: null == toBuyCount ? _self.toBuyCount : toBuyCount // ignore: cast_nullable_to_non_nullable
as int,scoreOverride: freezed == scoreOverride ? _self.scoreOverride : scoreOverride // ignore: cast_nullable_to_non_nullable
as int?,explanation: freezed == explanation ? _self.explanation : explanation // ignore: cast_nullable_to_non_nullable
as String?,isMock: null == isMock ? _self.isMock : isMock // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}
/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DishCopyWith<$Res> get dish {
  
  return $DishCopyWith<$Res>(_self.dish, (value) {
    return _then(_self.copyWith(dish: value));
  });
}/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ScoreBreakdownCopyWith<$Res> get breakdown {
  
  return $ScoreBreakdownCopyWith<$Res>(_self.breakdown, (value) {
    return _then(_self.copyWith(breakdown: value));
  });
}
}


/// Adds pattern-matching-related methods to [DishSuggestion].
extension DishSuggestionPatterns on DishSuggestion {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DishSuggestion value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DishSuggestion() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DishSuggestion value)  $default,){
final _that = this;
switch (_that) {
case _DishSuggestion():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DishSuggestion value)?  $default,){
final _that = this;
switch (_that) {
case _DishSuggestion() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( Dish dish,  ScoreBreakdown breakdown,  List<String> nearExpiryIngredients,  double availabilityRatio,  int toBuyCount,  int? scoreOverride,  String? explanation,  bool isMock)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DishSuggestion() when $default != null:
return $default(_that.dish,_that.breakdown,_that.nearExpiryIngredients,_that.availabilityRatio,_that.toBuyCount,_that.scoreOverride,_that.explanation,_that.isMock);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( Dish dish,  ScoreBreakdown breakdown,  List<String> nearExpiryIngredients,  double availabilityRatio,  int toBuyCount,  int? scoreOverride,  String? explanation,  bool isMock)  $default,) {final _that = this;
switch (_that) {
case _DishSuggestion():
return $default(_that.dish,_that.breakdown,_that.nearExpiryIngredients,_that.availabilityRatio,_that.toBuyCount,_that.scoreOverride,_that.explanation,_that.isMock);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( Dish dish,  ScoreBreakdown breakdown,  List<String> nearExpiryIngredients,  double availabilityRatio,  int toBuyCount,  int? scoreOverride,  String? explanation,  bool isMock)?  $default,) {final _that = this;
switch (_that) {
case _DishSuggestion() when $default != null:
return $default(_that.dish,_that.breakdown,_that.nearExpiryIngredients,_that.availabilityRatio,_that.toBuyCount,_that.scoreOverride,_that.explanation,_that.isMock);case _:
  return null;

}
}

}

/// @nodoc


class _DishSuggestion extends DishSuggestion {
  const _DishSuggestion({required this.dish, required this.breakdown, final  List<String> nearExpiryIngredients = const <String>[], this.availabilityRatio = 0, this.toBuyCount = 0, this.scoreOverride, this.explanation, this.isMock = false}): _nearExpiryIngredients = nearExpiryIngredients,super._();
  

@override final  Dish dish;
@override final  ScoreBreakdown breakdown;
/// Names of near-expiry pantry ingredients this dish would use.
 final  List<String> _nearExpiryIngredients;
/// Names of near-expiry pantry ingredients this dish would use.
@override@JsonKey() List<String> get nearExpiryIngredients {
  if (_nearExpiryIngredients is EqualUnmodifiableListView) return _nearExpiryIngredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_nearExpiryIngredients);
}

/// Share of the dish's ingredients already in the pantry (`0..1`).
@override@JsonKey() final  double availabilityRatio;
/// How many ingredients still need buying.
@override@JsonKey() final  int toBuyCount;
/// Server-provided score override; falls back to [breakdown.scoreOutOf100].
@override final  int? scoreOverride;
/// Human-readable explanation from recommendation engine / mock provider.
@override final  String? explanation;
/// True if the score and ranking are from a mock provider (`analysis.is_mock`).
@override@JsonKey() final  bool isMock;

/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DishSuggestionCopyWith<_DishSuggestion> get copyWith => __$DishSuggestionCopyWithImpl<_DishSuggestion>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DishSuggestion&&(identical(other.dish, dish) || other.dish == dish)&&(identical(other.breakdown, breakdown) || other.breakdown == breakdown)&&const DeepCollectionEquality().equals(other._nearExpiryIngredients, _nearExpiryIngredients)&&(identical(other.availabilityRatio, availabilityRatio) || other.availabilityRatio == availabilityRatio)&&(identical(other.toBuyCount, toBuyCount) || other.toBuyCount == toBuyCount)&&(identical(other.scoreOverride, scoreOverride) || other.scoreOverride == scoreOverride)&&(identical(other.explanation, explanation) || other.explanation == explanation)&&(identical(other.isMock, isMock) || other.isMock == isMock));
}


@override
int get hashCode => Object.hash(runtimeType,dish,breakdown,const DeepCollectionEquality().hash(_nearExpiryIngredients),availabilityRatio,toBuyCount,scoreOverride,explanation,isMock);

@override
String toString() {
  return 'DishSuggestion(dish: $dish, breakdown: $breakdown, nearExpiryIngredients: $nearExpiryIngredients, availabilityRatio: $availabilityRatio, toBuyCount: $toBuyCount, scoreOverride: $scoreOverride, explanation: $explanation, isMock: $isMock)';
}


}

/// @nodoc
abstract mixin class _$DishSuggestionCopyWith<$Res> implements $DishSuggestionCopyWith<$Res> {
  factory _$DishSuggestionCopyWith(_DishSuggestion value, $Res Function(_DishSuggestion) _then) = __$DishSuggestionCopyWithImpl;
@override @useResult
$Res call({
 Dish dish, ScoreBreakdown breakdown, List<String> nearExpiryIngredients, double availabilityRatio, int toBuyCount, int? scoreOverride, String? explanation, bool isMock
});


@override $DishCopyWith<$Res> get dish;@override $ScoreBreakdownCopyWith<$Res> get breakdown;

}
/// @nodoc
class __$DishSuggestionCopyWithImpl<$Res>
    implements _$DishSuggestionCopyWith<$Res> {
  __$DishSuggestionCopyWithImpl(this._self, this._then);

  final _DishSuggestion _self;
  final $Res Function(_DishSuggestion) _then;

/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? dish = null,Object? breakdown = null,Object? nearExpiryIngredients = null,Object? availabilityRatio = null,Object? toBuyCount = null,Object? scoreOverride = freezed,Object? explanation = freezed,Object? isMock = null,}) {
  return _then(_DishSuggestion(
dish: null == dish ? _self.dish : dish // ignore: cast_nullable_to_non_nullable
as Dish,breakdown: null == breakdown ? _self.breakdown : breakdown // ignore: cast_nullable_to_non_nullable
as ScoreBreakdown,nearExpiryIngredients: null == nearExpiryIngredients ? _self._nearExpiryIngredients : nearExpiryIngredients // ignore: cast_nullable_to_non_nullable
as List<String>,availabilityRatio: null == availabilityRatio ? _self.availabilityRatio : availabilityRatio // ignore: cast_nullable_to_non_nullable
as double,toBuyCount: null == toBuyCount ? _self.toBuyCount : toBuyCount // ignore: cast_nullable_to_non_nullable
as int,scoreOverride: freezed == scoreOverride ? _self.scoreOverride : scoreOverride // ignore: cast_nullable_to_non_nullable
as int?,explanation: freezed == explanation ? _self.explanation : explanation // ignore: cast_nullable_to_non_nullable
as String?,isMock: null == isMock ? _self.isMock : isMock // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DishCopyWith<$Res> get dish {
  
  return $DishCopyWith<$Res>(_self.dish, (value) {
    return _then(_self.copyWith(dish: value));
  });
}/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ScoreBreakdownCopyWith<$Res> get breakdown {
  
  return $ScoreBreakdownCopyWith<$Res>(_self.breakdown, (value) {
    return _then(_self.copyWith(breakdown: value));
  });
}
}

// dart format on
