// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ingredient.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$Ingredient {

 String get id; String get name; String get category; MeasurementUnit get defaultUnit; NutritionInfo? get nutritionPer100g;/// Reference storage guidance when the product has no printed HSD (spec 6.3.2).
 int? get referenceShelfLifeDays;
/// Create a copy of Ingredient
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$IngredientCopyWith<Ingredient> get copyWith => _$IngredientCopyWithImpl<Ingredient>(this as Ingredient, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Ingredient&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.defaultUnit, defaultUnit) || other.defaultUnit == defaultUnit)&&(identical(other.nutritionPer100g, nutritionPer100g) || other.nutritionPer100g == nutritionPer100g)&&(identical(other.referenceShelfLifeDays, referenceShelfLifeDays) || other.referenceShelfLifeDays == referenceShelfLifeDays));
}


@override
int get hashCode => Object.hash(runtimeType,id,name,category,defaultUnit,nutritionPer100g,referenceShelfLifeDays);

@override
String toString() {
  return 'Ingredient(id: $id, name: $name, category: $category, defaultUnit: $defaultUnit, nutritionPer100g: $nutritionPer100g, referenceShelfLifeDays: $referenceShelfLifeDays)';
}


}

/// @nodoc
abstract mixin class $IngredientCopyWith<$Res>  {
  factory $IngredientCopyWith(Ingredient value, $Res Function(Ingredient) _then) = _$IngredientCopyWithImpl;
@useResult
$Res call({
 String id, String name, String category, MeasurementUnit defaultUnit, NutritionInfo? nutritionPer100g, int? referenceShelfLifeDays
});




}
/// @nodoc
class _$IngredientCopyWithImpl<$Res>
    implements $IngredientCopyWith<$Res> {
  _$IngredientCopyWithImpl(this._self, this._then);

  final Ingredient _self;
  final $Res Function(Ingredient) _then;

/// Create a copy of Ingredient
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? category = null,Object? defaultUnit = null,Object? nutritionPer100g = freezed,Object? referenceShelfLifeDays = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,defaultUnit: null == defaultUnit ? _self.defaultUnit : defaultUnit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,nutritionPer100g: freezed == nutritionPer100g ? _self.nutritionPer100g : nutritionPer100g // ignore: cast_nullable_to_non_nullable
as NutritionInfo?,referenceShelfLifeDays: freezed == referenceShelfLifeDays ? _self.referenceShelfLifeDays : referenceShelfLifeDays // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [Ingredient].
extension IngredientPatterns on Ingredient {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Ingredient value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Ingredient() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Ingredient value)  $default,){
final _that = this;
switch (_that) {
case _Ingredient():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Ingredient value)?  $default,){
final _that = this;
switch (_that) {
case _Ingredient() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String category,  MeasurementUnit defaultUnit,  NutritionInfo? nutritionPer100g,  int? referenceShelfLifeDays)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Ingredient() when $default != null:
return $default(_that.id,_that.name,_that.category,_that.defaultUnit,_that.nutritionPer100g,_that.referenceShelfLifeDays);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String category,  MeasurementUnit defaultUnit,  NutritionInfo? nutritionPer100g,  int? referenceShelfLifeDays)  $default,) {final _that = this;
switch (_that) {
case _Ingredient():
return $default(_that.id,_that.name,_that.category,_that.defaultUnit,_that.nutritionPer100g,_that.referenceShelfLifeDays);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String category,  MeasurementUnit defaultUnit,  NutritionInfo? nutritionPer100g,  int? referenceShelfLifeDays)?  $default,) {final _that = this;
switch (_that) {
case _Ingredient() when $default != null:
return $default(_that.id,_that.name,_that.category,_that.defaultUnit,_that.nutritionPer100g,_that.referenceShelfLifeDays);case _:
  return null;

}
}

}

/// @nodoc


class _Ingredient implements Ingredient {
  const _Ingredient({required this.id, required this.name, required this.category, required this.defaultUnit, this.nutritionPer100g, this.referenceShelfLifeDays});
  

@override final  String id;
@override final  String name;
@override final  String category;
@override final  MeasurementUnit defaultUnit;
@override final  NutritionInfo? nutritionPer100g;
/// Reference storage guidance when the product has no printed HSD (spec 6.3.2).
@override final  int? referenceShelfLifeDays;

/// Create a copy of Ingredient
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$IngredientCopyWith<_Ingredient> get copyWith => __$IngredientCopyWithImpl<_Ingredient>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Ingredient&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.defaultUnit, defaultUnit) || other.defaultUnit == defaultUnit)&&(identical(other.nutritionPer100g, nutritionPer100g) || other.nutritionPer100g == nutritionPer100g)&&(identical(other.referenceShelfLifeDays, referenceShelfLifeDays) || other.referenceShelfLifeDays == referenceShelfLifeDays));
}


@override
int get hashCode => Object.hash(runtimeType,id,name,category,defaultUnit,nutritionPer100g,referenceShelfLifeDays);

@override
String toString() {
  return 'Ingredient(id: $id, name: $name, category: $category, defaultUnit: $defaultUnit, nutritionPer100g: $nutritionPer100g, referenceShelfLifeDays: $referenceShelfLifeDays)';
}


}

/// @nodoc
abstract mixin class _$IngredientCopyWith<$Res> implements $IngredientCopyWith<$Res> {
  factory _$IngredientCopyWith(_Ingredient value, $Res Function(_Ingredient) _then) = __$IngredientCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String category, MeasurementUnit defaultUnit, NutritionInfo? nutritionPer100g, int? referenceShelfLifeDays
});




}
/// @nodoc
class __$IngredientCopyWithImpl<$Res>
    implements _$IngredientCopyWith<$Res> {
  __$IngredientCopyWithImpl(this._self, this._then);

  final _Ingredient _self;
  final $Res Function(_Ingredient) _then;

/// Create a copy of Ingredient
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? category = null,Object? defaultUnit = null,Object? nutritionPer100g = freezed,Object? referenceShelfLifeDays = freezed,}) {
  return _then(_Ingredient(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,defaultUnit: null == defaultUnit ? _self.defaultUnit : defaultUnit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,nutritionPer100g: freezed == nutritionPer100g ? _self.nutritionPer100g : nutritionPer100g // ignore: cast_nullable_to_non_nullable
as NutritionInfo?,referenceShelfLifeDays: freezed == referenceShelfLifeDays ? _self.referenceShelfLifeDays : referenceShelfLifeDays // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}

// dart format on
