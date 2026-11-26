// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'nutrition_profile.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$NutritionProfile {

 int get householdSize; DietaryPreference get diet; List<HealthCondition> get healthConditions; List<AllergyGroup> get allergies; List<String> get dislikedIngredients;
/// Create a copy of NutritionProfile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$NutritionProfileCopyWith<NutritionProfile> get copyWith => _$NutritionProfileCopyWithImpl<NutritionProfile>(this as NutritionProfile, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is NutritionProfile&&(identical(other.householdSize, householdSize) || other.householdSize == householdSize)&&(identical(other.diet, diet) || other.diet == diet)&&const DeepCollectionEquality().equals(other.healthConditions, healthConditions)&&const DeepCollectionEquality().equals(other.allergies, allergies)&&const DeepCollectionEquality().equals(other.dislikedIngredients, dislikedIngredients));
}


@override
int get hashCode => Object.hash(runtimeType,householdSize,diet,const DeepCollectionEquality().hash(healthConditions),const DeepCollectionEquality().hash(allergies),const DeepCollectionEquality().hash(dislikedIngredients));

@override
String toString() {
  return 'NutritionProfile(householdSize: $householdSize, diet: $diet, healthConditions: $healthConditions, allergies: $allergies, dislikedIngredients: $dislikedIngredients)';
}


}

/// @nodoc
abstract mixin class $NutritionProfileCopyWith<$Res>  {
  factory $NutritionProfileCopyWith(NutritionProfile value, $Res Function(NutritionProfile) _then) = _$NutritionProfileCopyWithImpl;
@useResult
$Res call({
 int householdSize, DietaryPreference diet, List<HealthCondition> healthConditions, List<AllergyGroup> allergies, List<String> dislikedIngredients
});




}
/// @nodoc
class _$NutritionProfileCopyWithImpl<$Res>
    implements $NutritionProfileCopyWith<$Res> {
  _$NutritionProfileCopyWithImpl(this._self, this._then);

  final NutritionProfile _self;
  final $Res Function(NutritionProfile) _then;

/// Create a copy of NutritionProfile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? householdSize = null,Object? diet = null,Object? healthConditions = null,Object? allergies = null,Object? dislikedIngredients = null,}) {
  return _then(_self.copyWith(
householdSize: null == householdSize ? _self.householdSize : householdSize // ignore: cast_nullable_to_non_nullable
as int,diet: null == diet ? _self.diet : diet // ignore: cast_nullable_to_non_nullable
as DietaryPreference,healthConditions: null == healthConditions ? _self.healthConditions : healthConditions // ignore: cast_nullable_to_non_nullable
as List<HealthCondition>,allergies: null == allergies ? _self.allergies : allergies // ignore: cast_nullable_to_non_nullable
as List<AllergyGroup>,dislikedIngredients: null == dislikedIngredients ? _self.dislikedIngredients : dislikedIngredients // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// Adds pattern-matching-related methods to [NutritionProfile].
extension NutritionProfilePatterns on NutritionProfile {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _NutritionProfile value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _NutritionProfile() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _NutritionProfile value)  $default,){
final _that = this;
switch (_that) {
case _NutritionProfile():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _NutritionProfile value)?  $default,){
final _that = this;
switch (_that) {
case _NutritionProfile() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int householdSize,  DietaryPreference diet,  List<HealthCondition> healthConditions,  List<AllergyGroup> allergies,  List<String> dislikedIngredients)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _NutritionProfile() when $default != null:
return $default(_that.householdSize,_that.diet,_that.healthConditions,_that.allergies,_that.dislikedIngredients);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int householdSize,  DietaryPreference diet,  List<HealthCondition> healthConditions,  List<AllergyGroup> allergies,  List<String> dislikedIngredients)  $default,) {final _that = this;
switch (_that) {
case _NutritionProfile():
return $default(_that.householdSize,_that.diet,_that.healthConditions,_that.allergies,_that.dislikedIngredients);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int householdSize,  DietaryPreference diet,  List<HealthCondition> healthConditions,  List<AllergyGroup> allergies,  List<String> dislikedIngredients)?  $default,) {final _that = this;
switch (_that) {
case _NutritionProfile() when $default != null:
return $default(_that.householdSize,_that.diet,_that.healthConditions,_that.allergies,_that.dislikedIngredients);case _:
  return null;

}
}

}

/// @nodoc


class _NutritionProfile extends NutritionProfile {
  const _NutritionProfile({this.householdSize = NutritionProfile.defaultHouseholdSize, this.diet = DietaryPreference.balanced, final  List<HealthCondition> healthConditions = const <HealthCondition>[], final  List<AllergyGroup> allergies = const <AllergyGroup>[], final  List<String> dislikedIngredients = const <String>[]}): _healthConditions = healthConditions,_allergies = allergies,_dislikedIngredients = dislikedIngredients,super._();
  

@override@JsonKey() final  int householdSize;
@override@JsonKey() final  DietaryPreference diet;
 final  List<HealthCondition> _healthConditions;
@override@JsonKey() List<HealthCondition> get healthConditions {
  if (_healthConditions is EqualUnmodifiableListView) return _healthConditions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_healthConditions);
}

 final  List<AllergyGroup> _allergies;
@override@JsonKey() List<AllergyGroup> get allergies {
  if (_allergies is EqualUnmodifiableListView) return _allergies;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_allergies);
}

 final  List<String> _dislikedIngredients;
@override@JsonKey() List<String> get dislikedIngredients {
  if (_dislikedIngredients is EqualUnmodifiableListView) return _dislikedIngredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_dislikedIngredients);
}


/// Create a copy of NutritionProfile
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$NutritionProfileCopyWith<_NutritionProfile> get copyWith => __$NutritionProfileCopyWithImpl<_NutritionProfile>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _NutritionProfile&&(identical(other.householdSize, householdSize) || other.householdSize == householdSize)&&(identical(other.diet, diet) || other.diet == diet)&&const DeepCollectionEquality().equals(other._healthConditions, _healthConditions)&&const DeepCollectionEquality().equals(other._allergies, _allergies)&&const DeepCollectionEquality().equals(other._dislikedIngredients, _dislikedIngredients));
}


@override
int get hashCode => Object.hash(runtimeType,householdSize,diet,const DeepCollectionEquality().hash(_healthConditions),const DeepCollectionEquality().hash(_allergies),const DeepCollectionEquality().hash(_dislikedIngredients));

@override
String toString() {
  return 'NutritionProfile(householdSize: $householdSize, diet: $diet, healthConditions: $healthConditions, allergies: $allergies, dislikedIngredients: $dislikedIngredients)';
}


}

/// @nodoc
abstract mixin class _$NutritionProfileCopyWith<$Res> implements $NutritionProfileCopyWith<$Res> {
  factory _$NutritionProfileCopyWith(_NutritionProfile value, $Res Function(_NutritionProfile) _then) = __$NutritionProfileCopyWithImpl;
@override @useResult
$Res call({
 int householdSize, DietaryPreference diet, List<HealthCondition> healthConditions, List<AllergyGroup> allergies, List<String> dislikedIngredients
});




}
/// @nodoc
class __$NutritionProfileCopyWithImpl<$Res>
    implements _$NutritionProfileCopyWith<$Res> {
  __$NutritionProfileCopyWithImpl(this._self, this._then);

  final _NutritionProfile _self;
  final $Res Function(_NutritionProfile) _then;

/// Create a copy of NutritionProfile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? householdSize = null,Object? diet = null,Object? healthConditions = null,Object? allergies = null,Object? dislikedIngredients = null,}) {
  return _then(_NutritionProfile(
householdSize: null == householdSize ? _self.householdSize : householdSize // ignore: cast_nullable_to_non_nullable
as int,diet: null == diet ? _self.diet : diet // ignore: cast_nullable_to_non_nullable
as DietaryPreference,healthConditions: null == healthConditions ? _self._healthConditions : healthConditions // ignore: cast_nullable_to_non_nullable
as List<HealthCondition>,allergies: null == allergies ? _self._allergies : allergies // ignore: cast_nullable_to_non_nullable
as List<AllergyGroup>,dislikedIngredients: null == dislikedIngredients ? _self._dislikedIngredients : dislikedIngredients // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

// dart format on
