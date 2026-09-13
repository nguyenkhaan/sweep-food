// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'dish_suggestion_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$DishSuggestionDto {

 DishDto get dish; ScoreBreakdownDto? get breakdown;@JsonKey(name: 'near_expiry_ingredients') List<String> get nearExpiryIngredients;@JsonKey(name: 'availability_ratio') double get availabilityRatio;@JsonKey(name: 'to_buy_count') int get toBuyCount; int? get score;
/// Create a copy of DishSuggestionDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DishSuggestionDtoCopyWith<DishSuggestionDto> get copyWith => _$DishSuggestionDtoCopyWithImpl<DishSuggestionDto>(this as DishSuggestionDto, _$identity);

  /// Serializes this DishSuggestionDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DishSuggestionDto&&(identical(other.dish, dish) || other.dish == dish)&&(identical(other.breakdown, breakdown) || other.breakdown == breakdown)&&const DeepCollectionEquality().equals(other.nearExpiryIngredients, nearExpiryIngredients)&&(identical(other.availabilityRatio, availabilityRatio) || other.availabilityRatio == availabilityRatio)&&(identical(other.toBuyCount, toBuyCount) || other.toBuyCount == toBuyCount)&&(identical(other.score, score) || other.score == score));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,dish,breakdown,const DeepCollectionEquality().hash(nearExpiryIngredients),availabilityRatio,toBuyCount,score);

@override
String toString() {
  return 'DishSuggestionDto(dish: $dish, breakdown: $breakdown, nearExpiryIngredients: $nearExpiryIngredients, availabilityRatio: $availabilityRatio, toBuyCount: $toBuyCount, score: $score)';
}


}

/// @nodoc
abstract mixin class $DishSuggestionDtoCopyWith<$Res>  {
  factory $DishSuggestionDtoCopyWith(DishSuggestionDto value, $Res Function(DishSuggestionDto) _then) = _$DishSuggestionDtoCopyWithImpl;
@useResult
$Res call({
 DishDto dish, ScoreBreakdownDto? breakdown,@JsonKey(name: 'near_expiry_ingredients') List<String> nearExpiryIngredients,@JsonKey(name: 'availability_ratio') double availabilityRatio,@JsonKey(name: 'to_buy_count') int toBuyCount, int? score
});


$DishDtoCopyWith<$Res> get dish;$ScoreBreakdownDtoCopyWith<$Res>? get breakdown;

}
/// @nodoc
class _$DishSuggestionDtoCopyWithImpl<$Res>
    implements $DishSuggestionDtoCopyWith<$Res> {
  _$DishSuggestionDtoCopyWithImpl(this._self, this._then);

  final DishSuggestionDto _self;
  final $Res Function(DishSuggestionDto) _then;

/// Create a copy of DishSuggestionDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? dish = null,Object? breakdown = freezed,Object? nearExpiryIngredients = null,Object? availabilityRatio = null,Object? toBuyCount = null,Object? score = freezed,}) {
  return _then(_self.copyWith(
dish: null == dish ? _self.dish : dish // ignore: cast_nullable_to_non_nullable
as DishDto,breakdown: freezed == breakdown ? _self.breakdown : breakdown // ignore: cast_nullable_to_non_nullable
as ScoreBreakdownDto?,nearExpiryIngredients: null == nearExpiryIngredients ? _self.nearExpiryIngredients : nearExpiryIngredients // ignore: cast_nullable_to_non_nullable
as List<String>,availabilityRatio: null == availabilityRatio ? _self.availabilityRatio : availabilityRatio // ignore: cast_nullable_to_non_nullable
as double,toBuyCount: null == toBuyCount ? _self.toBuyCount : toBuyCount // ignore: cast_nullable_to_non_nullable
as int,score: freezed == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}
/// Create a copy of DishSuggestionDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DishDtoCopyWith<$Res> get dish {
  
  return $DishDtoCopyWith<$Res>(_self.dish, (value) {
    return _then(_self.copyWith(dish: value));
  });
}/// Create a copy of DishSuggestionDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ScoreBreakdownDtoCopyWith<$Res>? get breakdown {
    if (_self.breakdown == null) {
    return null;
  }

  return $ScoreBreakdownDtoCopyWith<$Res>(_self.breakdown!, (value) {
    return _then(_self.copyWith(breakdown: value));
  });
}
}


/// Adds pattern-matching-related methods to [DishSuggestionDto].
extension DishSuggestionDtoPatterns on DishSuggestionDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DishSuggestionDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DishSuggestionDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DishSuggestionDto value)  $default,){
final _that = this;
switch (_that) {
case _DishSuggestionDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DishSuggestionDto value)?  $default,){
final _that = this;
switch (_that) {
case _DishSuggestionDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( DishDto dish,  ScoreBreakdownDto? breakdown, @JsonKey(name: 'near_expiry_ingredients')  List<String> nearExpiryIngredients, @JsonKey(name: 'availability_ratio')  double availabilityRatio, @JsonKey(name: 'to_buy_count')  int toBuyCount,  int? score)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DishSuggestionDto() when $default != null:
return $default(_that.dish,_that.breakdown,_that.nearExpiryIngredients,_that.availabilityRatio,_that.toBuyCount,_that.score);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( DishDto dish,  ScoreBreakdownDto? breakdown, @JsonKey(name: 'near_expiry_ingredients')  List<String> nearExpiryIngredients, @JsonKey(name: 'availability_ratio')  double availabilityRatio, @JsonKey(name: 'to_buy_count')  int toBuyCount,  int? score)  $default,) {final _that = this;
switch (_that) {
case _DishSuggestionDto():
return $default(_that.dish,_that.breakdown,_that.nearExpiryIngredients,_that.availabilityRatio,_that.toBuyCount,_that.score);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( DishDto dish,  ScoreBreakdownDto? breakdown, @JsonKey(name: 'near_expiry_ingredients')  List<String> nearExpiryIngredients, @JsonKey(name: 'availability_ratio')  double availabilityRatio, @JsonKey(name: 'to_buy_count')  int toBuyCount,  int? score)?  $default,) {final _that = this;
switch (_that) {
case _DishSuggestionDto() when $default != null:
return $default(_that.dish,_that.breakdown,_that.nearExpiryIngredients,_that.availabilityRatio,_that.toBuyCount,_that.score);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _DishSuggestionDto extends DishSuggestionDto {
  const _DishSuggestionDto({required this.dish, this.breakdown, @JsonKey(name: 'near_expiry_ingredients') final  List<String> nearExpiryIngredients = const <String>[], @JsonKey(name: 'availability_ratio') this.availabilityRatio = 0, @JsonKey(name: 'to_buy_count') this.toBuyCount = 0, this.score}): _nearExpiryIngredients = nearExpiryIngredients,super._();
  factory _DishSuggestionDto.fromJson(Map<String, dynamic> json) => _$DishSuggestionDtoFromJson(json);

@override final  DishDto dish;
@override final  ScoreBreakdownDto? breakdown;
 final  List<String> _nearExpiryIngredients;
@override@JsonKey(name: 'near_expiry_ingredients') List<String> get nearExpiryIngredients {
  if (_nearExpiryIngredients is EqualUnmodifiableListView) return _nearExpiryIngredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_nearExpiryIngredients);
}

@override@JsonKey(name: 'availability_ratio') final  double availabilityRatio;
@override@JsonKey(name: 'to_buy_count') final  int toBuyCount;
@override final  int? score;

/// Create a copy of DishSuggestionDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DishSuggestionDtoCopyWith<_DishSuggestionDto> get copyWith => __$DishSuggestionDtoCopyWithImpl<_DishSuggestionDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DishSuggestionDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DishSuggestionDto&&(identical(other.dish, dish) || other.dish == dish)&&(identical(other.breakdown, breakdown) || other.breakdown == breakdown)&&const DeepCollectionEquality().equals(other._nearExpiryIngredients, _nearExpiryIngredients)&&(identical(other.availabilityRatio, availabilityRatio) || other.availabilityRatio == availabilityRatio)&&(identical(other.toBuyCount, toBuyCount) || other.toBuyCount == toBuyCount)&&(identical(other.score, score) || other.score == score));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,dish,breakdown,const DeepCollectionEquality().hash(_nearExpiryIngredients),availabilityRatio,toBuyCount,score);

@override
String toString() {
  return 'DishSuggestionDto(dish: $dish, breakdown: $breakdown, nearExpiryIngredients: $nearExpiryIngredients, availabilityRatio: $availabilityRatio, toBuyCount: $toBuyCount, score: $score)';
}


}

/// @nodoc
abstract mixin class _$DishSuggestionDtoCopyWith<$Res> implements $DishSuggestionDtoCopyWith<$Res> {
  factory _$DishSuggestionDtoCopyWith(_DishSuggestionDto value, $Res Function(_DishSuggestionDto) _then) = __$DishSuggestionDtoCopyWithImpl;
@override @useResult
$Res call({
 DishDto dish, ScoreBreakdownDto? breakdown,@JsonKey(name: 'near_expiry_ingredients') List<String> nearExpiryIngredients,@JsonKey(name: 'availability_ratio') double availabilityRatio,@JsonKey(name: 'to_buy_count') int toBuyCount, int? score
});


@override $DishDtoCopyWith<$Res> get dish;@override $ScoreBreakdownDtoCopyWith<$Res>? get breakdown;

}
/// @nodoc
class __$DishSuggestionDtoCopyWithImpl<$Res>
    implements _$DishSuggestionDtoCopyWith<$Res> {
  __$DishSuggestionDtoCopyWithImpl(this._self, this._then);

  final _DishSuggestionDto _self;
  final $Res Function(_DishSuggestionDto) _then;

/// Create a copy of DishSuggestionDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? dish = null,Object? breakdown = freezed,Object? nearExpiryIngredients = null,Object? availabilityRatio = null,Object? toBuyCount = null,Object? score = freezed,}) {
  return _then(_DishSuggestionDto(
dish: null == dish ? _self.dish : dish // ignore: cast_nullable_to_non_nullable
as DishDto,breakdown: freezed == breakdown ? _self.breakdown : breakdown // ignore: cast_nullable_to_non_nullable
as ScoreBreakdownDto?,nearExpiryIngredients: null == nearExpiryIngredients ? _self._nearExpiryIngredients : nearExpiryIngredients // ignore: cast_nullable_to_non_nullable
as List<String>,availabilityRatio: null == availabilityRatio ? _self.availabilityRatio : availabilityRatio // ignore: cast_nullable_to_non_nullable
as double,toBuyCount: null == toBuyCount ? _self.toBuyCount : toBuyCount // ignore: cast_nullable_to_non_nullable
as int,score: freezed == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

/// Create a copy of DishSuggestionDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DishDtoCopyWith<$Res> get dish {
  
  return $DishDtoCopyWith<$Res>(_self.dish, (value) {
    return _then(_self.copyWith(dish: value));
  });
}/// Create a copy of DishSuggestionDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ScoreBreakdownDtoCopyWith<$Res>? get breakdown {
    if (_self.breakdown == null) {
    return null;
  }

  return $ScoreBreakdownDtoCopyWith<$Res>(_self.breakdown!, (value) {
    return _then(_self.copyWith(breakdown: value));
  });
}
}


/// @nodoc
mixin _$ScoreBreakdownDto {

 double get e; double get a; double get p; double get u;
/// Create a copy of ScoreBreakdownDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ScoreBreakdownDtoCopyWith<ScoreBreakdownDto> get copyWith => _$ScoreBreakdownDtoCopyWithImpl<ScoreBreakdownDto>(this as ScoreBreakdownDto, _$identity);

  /// Serializes this ScoreBreakdownDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ScoreBreakdownDto&&(identical(other.e, e) || other.e == e)&&(identical(other.a, a) || other.a == a)&&(identical(other.p, p) || other.p == p)&&(identical(other.u, u) || other.u == u));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,e,a,p,u);

@override
String toString() {
  return 'ScoreBreakdownDto(e: $e, a: $a, p: $p, u: $u)';
}


}

/// @nodoc
abstract mixin class $ScoreBreakdownDtoCopyWith<$Res>  {
  factory $ScoreBreakdownDtoCopyWith(ScoreBreakdownDto value, $Res Function(ScoreBreakdownDto) _then) = _$ScoreBreakdownDtoCopyWithImpl;
@useResult
$Res call({
 double e, double a, double p, double u
});




}
/// @nodoc
class _$ScoreBreakdownDtoCopyWithImpl<$Res>
    implements $ScoreBreakdownDtoCopyWith<$Res> {
  _$ScoreBreakdownDtoCopyWithImpl(this._self, this._then);

  final ScoreBreakdownDto _self;
  final $Res Function(ScoreBreakdownDto) _then;

/// Create a copy of ScoreBreakdownDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? e = null,Object? a = null,Object? p = null,Object? u = null,}) {
  return _then(_self.copyWith(
e: null == e ? _self.e : e // ignore: cast_nullable_to_non_nullable
as double,a: null == a ? _self.a : a // ignore: cast_nullable_to_non_nullable
as double,p: null == p ? _self.p : p // ignore: cast_nullable_to_non_nullable
as double,u: null == u ? _self.u : u // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

}


/// Adds pattern-matching-related methods to [ScoreBreakdownDto].
extension ScoreBreakdownDtoPatterns on ScoreBreakdownDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ScoreBreakdownDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ScoreBreakdownDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ScoreBreakdownDto value)  $default,){
final _that = this;
switch (_that) {
case _ScoreBreakdownDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ScoreBreakdownDto value)?  $default,){
final _that = this;
switch (_that) {
case _ScoreBreakdownDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( double e,  double a,  double p,  double u)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ScoreBreakdownDto() when $default != null:
return $default(_that.e,_that.a,_that.p,_that.u);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( double e,  double a,  double p,  double u)  $default,) {final _that = this;
switch (_that) {
case _ScoreBreakdownDto():
return $default(_that.e,_that.a,_that.p,_that.u);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( double e,  double a,  double p,  double u)?  $default,) {final _that = this;
switch (_that) {
case _ScoreBreakdownDto() when $default != null:
return $default(_that.e,_that.a,_that.p,_that.u);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ScoreBreakdownDto extends ScoreBreakdownDto {
  const _ScoreBreakdownDto({this.e = 0, this.a = 0, this.p = 0, this.u = 0}): super._();
  factory _ScoreBreakdownDto.fromJson(Map<String, dynamic> json) => _$ScoreBreakdownDtoFromJson(json);

@override@JsonKey() final  double e;
@override@JsonKey() final  double a;
@override@JsonKey() final  double p;
@override@JsonKey() final  double u;

/// Create a copy of ScoreBreakdownDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ScoreBreakdownDtoCopyWith<_ScoreBreakdownDto> get copyWith => __$ScoreBreakdownDtoCopyWithImpl<_ScoreBreakdownDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ScoreBreakdownDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ScoreBreakdownDto&&(identical(other.e, e) || other.e == e)&&(identical(other.a, a) || other.a == a)&&(identical(other.p, p) || other.p == p)&&(identical(other.u, u) || other.u == u));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,e,a,p,u);

@override
String toString() {
  return 'ScoreBreakdownDto(e: $e, a: $a, p: $p, u: $u)';
}


}

/// @nodoc
abstract mixin class _$ScoreBreakdownDtoCopyWith<$Res> implements $ScoreBreakdownDtoCopyWith<$Res> {
  factory _$ScoreBreakdownDtoCopyWith(_ScoreBreakdownDto value, $Res Function(_ScoreBreakdownDto) _then) = __$ScoreBreakdownDtoCopyWithImpl;
@override @useResult
$Res call({
 double e, double a, double p, double u
});




}
/// @nodoc
class __$ScoreBreakdownDtoCopyWithImpl<$Res>
    implements _$ScoreBreakdownDtoCopyWith<$Res> {
  __$ScoreBreakdownDtoCopyWithImpl(this._self, this._then);

  final _ScoreBreakdownDto _self;
  final $Res Function(_ScoreBreakdownDto) _then;

/// Create a copy of ScoreBreakdownDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? e = null,Object? a = null,Object? p = null,Object? u = null,}) {
  return _then(_ScoreBreakdownDto(
e: null == e ? _self.e : e // ignore: cast_nullable_to_non_nullable
as double,a: null == a ? _self.a : a // ignore: cast_nullable_to_non_nullable
as double,p: null == p ? _self.p : p // ignore: cast_nullable_to_non_nullable
as double,u: null == u ? _self.u : u // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}

// dart format on
