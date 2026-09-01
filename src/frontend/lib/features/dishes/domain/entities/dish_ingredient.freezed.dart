// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'dish_ingredient.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$DishIngredient {

 String get name; double get quantity; MeasurementUnit get unit;/// Salt / pepper / fish sauce — shown as chips, never "cần mua".
 bool get isSeasoning;/// The kitchen already has enough of this.
 bool get availableInPantry;/// How much still needs buying (0 when [availableInPantry]).
 double get missingQty;/// The matching pantry batch is near its expiry date — drives the "cận hạn"
/// tag and the `E` term of the suggestion score.
 bool get nearExpiry;/// The pantry item this maps to, when matched.
 String? get pantryItemId;
/// Create a copy of DishIngredient
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DishIngredientCopyWith<DishIngredient> get copyWith => _$DishIngredientCopyWithImpl<DishIngredient>(this as DishIngredient, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DishIngredient&&(identical(other.name, name) || other.name == name)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.isSeasoning, isSeasoning) || other.isSeasoning == isSeasoning)&&(identical(other.availableInPantry, availableInPantry) || other.availableInPantry == availableInPantry)&&(identical(other.missingQty, missingQty) || other.missingQty == missingQty)&&(identical(other.nearExpiry, nearExpiry) || other.nearExpiry == nearExpiry)&&(identical(other.pantryItemId, pantryItemId) || other.pantryItemId == pantryItemId));
}


@override
int get hashCode => Object.hash(runtimeType,name,quantity,unit,isSeasoning,availableInPantry,missingQty,nearExpiry,pantryItemId);

@override
String toString() {
  return 'DishIngredient(name: $name, quantity: $quantity, unit: $unit, isSeasoning: $isSeasoning, availableInPantry: $availableInPantry, missingQty: $missingQty, nearExpiry: $nearExpiry, pantryItemId: $pantryItemId)';
}


}

/// @nodoc
abstract mixin class $DishIngredientCopyWith<$Res>  {
  factory $DishIngredientCopyWith(DishIngredient value, $Res Function(DishIngredient) _then) = _$DishIngredientCopyWithImpl;
@useResult
$Res call({
 String name, double quantity, MeasurementUnit unit, bool isSeasoning, bool availableInPantry, double missingQty, bool nearExpiry, String? pantryItemId
});




}
/// @nodoc
class _$DishIngredientCopyWithImpl<$Res>
    implements $DishIngredientCopyWith<$Res> {
  _$DishIngredientCopyWithImpl(this._self, this._then);

  final DishIngredient _self;
  final $Res Function(DishIngredient) _then;

/// Create a copy of DishIngredient
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? quantity = null,Object? unit = null,Object? isSeasoning = null,Object? availableInPantry = null,Object? missingQty = null,Object? nearExpiry = null,Object? pantryItemId = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,isSeasoning: null == isSeasoning ? _self.isSeasoning : isSeasoning // ignore: cast_nullable_to_non_nullable
as bool,availableInPantry: null == availableInPantry ? _self.availableInPantry : availableInPantry // ignore: cast_nullable_to_non_nullable
as bool,missingQty: null == missingQty ? _self.missingQty : missingQty // ignore: cast_nullable_to_non_nullable
as double,nearExpiry: null == nearExpiry ? _self.nearExpiry : nearExpiry // ignore: cast_nullable_to_non_nullable
as bool,pantryItemId: freezed == pantryItemId ? _self.pantryItemId : pantryItemId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [DishIngredient].
extension DishIngredientPatterns on DishIngredient {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DishIngredient value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DishIngredient() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DishIngredient value)  $default,){
final _that = this;
switch (_that) {
case _DishIngredient():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DishIngredient value)?  $default,){
final _that = this;
switch (_that) {
case _DishIngredient() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String name,  double quantity,  MeasurementUnit unit,  bool isSeasoning,  bool availableInPantry,  double missingQty,  bool nearExpiry,  String? pantryItemId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DishIngredient() when $default != null:
return $default(_that.name,_that.quantity,_that.unit,_that.isSeasoning,_that.availableInPantry,_that.missingQty,_that.nearExpiry,_that.pantryItemId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String name,  double quantity,  MeasurementUnit unit,  bool isSeasoning,  bool availableInPantry,  double missingQty,  bool nearExpiry,  String? pantryItemId)  $default,) {final _that = this;
switch (_that) {
case _DishIngredient():
return $default(_that.name,_that.quantity,_that.unit,_that.isSeasoning,_that.availableInPantry,_that.missingQty,_that.nearExpiry,_that.pantryItemId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String name,  double quantity,  MeasurementUnit unit,  bool isSeasoning,  bool availableInPantry,  double missingQty,  bool nearExpiry,  String? pantryItemId)?  $default,) {final _that = this;
switch (_that) {
case _DishIngredient() when $default != null:
return $default(_that.name,_that.quantity,_that.unit,_that.isSeasoning,_that.availableInPantry,_that.missingQty,_that.nearExpiry,_that.pantryItemId);case _:
  return null;

}
}

}

/// @nodoc


class _DishIngredient extends DishIngredient {
  const _DishIngredient({required this.name, required this.quantity, required this.unit, this.isSeasoning = false, this.availableInPantry = false, this.missingQty = 0, this.nearExpiry = false, this.pantryItemId}): super._();
  

@override final  String name;
@override final  double quantity;
@override final  MeasurementUnit unit;
/// Salt / pepper / fish sauce — shown as chips, never "cần mua".
@override@JsonKey() final  bool isSeasoning;
/// The kitchen already has enough of this.
@override@JsonKey() final  bool availableInPantry;
/// How much still needs buying (0 when [availableInPantry]).
@override@JsonKey() final  double missingQty;
/// The matching pantry batch is near its expiry date — drives the "cận hạn"
/// tag and the `E` term of the suggestion score.
@override@JsonKey() final  bool nearExpiry;
/// The pantry item this maps to, when matched.
@override final  String? pantryItemId;

/// Create a copy of DishIngredient
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DishIngredientCopyWith<_DishIngredient> get copyWith => __$DishIngredientCopyWithImpl<_DishIngredient>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DishIngredient&&(identical(other.name, name) || other.name == name)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.isSeasoning, isSeasoning) || other.isSeasoning == isSeasoning)&&(identical(other.availableInPantry, availableInPantry) || other.availableInPantry == availableInPantry)&&(identical(other.missingQty, missingQty) || other.missingQty == missingQty)&&(identical(other.nearExpiry, nearExpiry) || other.nearExpiry == nearExpiry)&&(identical(other.pantryItemId, pantryItemId) || other.pantryItemId == pantryItemId));
}


@override
int get hashCode => Object.hash(runtimeType,name,quantity,unit,isSeasoning,availableInPantry,missingQty,nearExpiry,pantryItemId);

@override
String toString() {
  return 'DishIngredient(name: $name, quantity: $quantity, unit: $unit, isSeasoning: $isSeasoning, availableInPantry: $availableInPantry, missingQty: $missingQty, nearExpiry: $nearExpiry, pantryItemId: $pantryItemId)';
}


}

/// @nodoc
abstract mixin class _$DishIngredientCopyWith<$Res> implements $DishIngredientCopyWith<$Res> {
  factory _$DishIngredientCopyWith(_DishIngredient value, $Res Function(_DishIngredient) _then) = __$DishIngredientCopyWithImpl;
@override @useResult
$Res call({
 String name, double quantity, MeasurementUnit unit, bool isSeasoning, bool availableInPantry, double missingQty, bool nearExpiry, String? pantryItemId
});




}
/// @nodoc
class __$DishIngredientCopyWithImpl<$Res>
    implements _$DishIngredientCopyWith<$Res> {
  __$DishIngredientCopyWithImpl(this._self, this._then);

  final _DishIngredient _self;
  final $Res Function(_DishIngredient) _then;

/// Create a copy of DishIngredient
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? quantity = null,Object? unit = null,Object? isSeasoning = null,Object? availableInPantry = null,Object? missingQty = null,Object? nearExpiry = null,Object? pantryItemId = freezed,}) {
  return _then(_DishIngredient(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,isSeasoning: null == isSeasoning ? _self.isSeasoning : isSeasoning // ignore: cast_nullable_to_non_nullable
as bool,availableInPantry: null == availableInPantry ? _self.availableInPantry : availableInPantry // ignore: cast_nullable_to_non_nullable
as bool,missingQty: null == missingQty ? _self.missingQty : missingQty // ignore: cast_nullable_to_non_nullable
as double,nearExpiry: null == nearExpiry ? _self.nearExpiry : nearExpiry // ignore: cast_nullable_to_non_nullable
as bool,pantryItemId: freezed == pantryItemId ? _self.pantryItemId : pantryItemId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
