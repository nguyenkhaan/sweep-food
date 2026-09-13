// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'recipe_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$RecipeDto {

 String get id; String get name; String get description;@JsonKey(name: 'media_url') String? get mediaUrl;@JsonKey(name: 'default_servings', fromJson: _asDouble) double? get defaultServings;@JsonKey(name: 'estimated_cooking_minutes') int get estimatedCookingMinutes;@JsonKey(name: 'estimated_cost', fromJson: _asDouble) double? get estimatedCost;// Detail-only fields (absent on the list endpoint).
@JsonKey(fromJson: _asDouble) double? get servings; Map<String, dynamic>? get instructions; RecipeNutritionDto? get nutrition; List<RecipeIngredientDto> get ingredients;
/// Create a copy of RecipeDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecipeDtoCopyWith<RecipeDto> get copyWith => _$RecipeDtoCopyWithImpl<RecipeDto>(this as RecipeDto, _$identity);

  /// Serializes this RecipeDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RecipeDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.mediaUrl, mediaUrl) || other.mediaUrl == mediaUrl)&&(identical(other.defaultServings, defaultServings) || other.defaultServings == defaultServings)&&(identical(other.estimatedCookingMinutes, estimatedCookingMinutes) || other.estimatedCookingMinutes == estimatedCookingMinutes)&&(identical(other.estimatedCost, estimatedCost) || other.estimatedCost == estimatedCost)&&(identical(other.servings, servings) || other.servings == servings)&&const DeepCollectionEquality().equals(other.instructions, instructions)&&(identical(other.nutrition, nutrition) || other.nutrition == nutrition)&&const DeepCollectionEquality().equals(other.ingredients, ingredients));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,mediaUrl,defaultServings,estimatedCookingMinutes,estimatedCost,servings,const DeepCollectionEquality().hash(instructions),nutrition,const DeepCollectionEquality().hash(ingredients));

@override
String toString() {
  return 'RecipeDto(id: $id, name: $name, description: $description, mediaUrl: $mediaUrl, defaultServings: $defaultServings, estimatedCookingMinutes: $estimatedCookingMinutes, estimatedCost: $estimatedCost, servings: $servings, instructions: $instructions, nutrition: $nutrition, ingredients: $ingredients)';
}


}

/// @nodoc
abstract mixin class $RecipeDtoCopyWith<$Res>  {
  factory $RecipeDtoCopyWith(RecipeDto value, $Res Function(RecipeDto) _then) = _$RecipeDtoCopyWithImpl;
@useResult
$Res call({
 String id, String name, String description,@JsonKey(name: 'media_url') String? mediaUrl,@JsonKey(name: 'default_servings', fromJson: _asDouble) double? defaultServings,@JsonKey(name: 'estimated_cooking_minutes') int estimatedCookingMinutes,@JsonKey(name: 'estimated_cost', fromJson: _asDouble) double? estimatedCost,@JsonKey(fromJson: _asDouble) double? servings, Map<String, dynamic>? instructions, RecipeNutritionDto? nutrition, List<RecipeIngredientDto> ingredients
});


$RecipeNutritionDtoCopyWith<$Res>? get nutrition;

}
/// @nodoc
class _$RecipeDtoCopyWithImpl<$Res>
    implements $RecipeDtoCopyWith<$Res> {
  _$RecipeDtoCopyWithImpl(this._self, this._then);

  final RecipeDto _self;
  final $Res Function(RecipeDto) _then;

/// Create a copy of RecipeDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = null,Object? mediaUrl = freezed,Object? defaultServings = freezed,Object? estimatedCookingMinutes = null,Object? estimatedCost = freezed,Object? servings = freezed,Object? instructions = freezed,Object? nutrition = freezed,Object? ingredients = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,mediaUrl: freezed == mediaUrl ? _self.mediaUrl : mediaUrl // ignore: cast_nullable_to_non_nullable
as String?,defaultServings: freezed == defaultServings ? _self.defaultServings : defaultServings // ignore: cast_nullable_to_non_nullable
as double?,estimatedCookingMinutes: null == estimatedCookingMinutes ? _self.estimatedCookingMinutes : estimatedCookingMinutes // ignore: cast_nullable_to_non_nullable
as int,estimatedCost: freezed == estimatedCost ? _self.estimatedCost : estimatedCost // ignore: cast_nullable_to_non_nullable
as double?,servings: freezed == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double?,instructions: freezed == instructions ? _self.instructions : instructions // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,nutrition: freezed == nutrition ? _self.nutrition : nutrition // ignore: cast_nullable_to_non_nullable
as RecipeNutritionDto?,ingredients: null == ingredients ? _self.ingredients : ingredients // ignore: cast_nullable_to_non_nullable
as List<RecipeIngredientDto>,
  ));
}
/// Create a copy of RecipeDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RecipeNutritionDtoCopyWith<$Res>? get nutrition {
    if (_self.nutrition == null) {
    return null;
  }

  return $RecipeNutritionDtoCopyWith<$Res>(_self.nutrition!, (value) {
    return _then(_self.copyWith(nutrition: value));
  });
}
}


/// Adds pattern-matching-related methods to [RecipeDto].
extension RecipeDtoPatterns on RecipeDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RecipeDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RecipeDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RecipeDto value)  $default,){
final _that = this;
switch (_that) {
case _RecipeDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RecipeDto value)?  $default,){
final _that = this;
switch (_that) {
case _RecipeDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String description, @JsonKey(name: 'media_url')  String? mediaUrl, @JsonKey(name: 'default_servings', fromJson: _asDouble)  double? defaultServings, @JsonKey(name: 'estimated_cooking_minutes')  int estimatedCookingMinutes, @JsonKey(name: 'estimated_cost', fromJson: _asDouble)  double? estimatedCost, @JsonKey(fromJson: _asDouble)  double? servings,  Map<String, dynamic>? instructions,  RecipeNutritionDto? nutrition,  List<RecipeIngredientDto> ingredients)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RecipeDto() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.mediaUrl,_that.defaultServings,_that.estimatedCookingMinutes,_that.estimatedCost,_that.servings,_that.instructions,_that.nutrition,_that.ingredients);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String description, @JsonKey(name: 'media_url')  String? mediaUrl, @JsonKey(name: 'default_servings', fromJson: _asDouble)  double? defaultServings, @JsonKey(name: 'estimated_cooking_minutes')  int estimatedCookingMinutes, @JsonKey(name: 'estimated_cost', fromJson: _asDouble)  double? estimatedCost, @JsonKey(fromJson: _asDouble)  double? servings,  Map<String, dynamic>? instructions,  RecipeNutritionDto? nutrition,  List<RecipeIngredientDto> ingredients)  $default,) {final _that = this;
switch (_that) {
case _RecipeDto():
return $default(_that.id,_that.name,_that.description,_that.mediaUrl,_that.defaultServings,_that.estimatedCookingMinutes,_that.estimatedCost,_that.servings,_that.instructions,_that.nutrition,_that.ingredients);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String description, @JsonKey(name: 'media_url')  String? mediaUrl, @JsonKey(name: 'default_servings', fromJson: _asDouble)  double? defaultServings, @JsonKey(name: 'estimated_cooking_minutes')  int estimatedCookingMinutes, @JsonKey(name: 'estimated_cost', fromJson: _asDouble)  double? estimatedCost, @JsonKey(fromJson: _asDouble)  double? servings,  Map<String, dynamic>? instructions,  RecipeNutritionDto? nutrition,  List<RecipeIngredientDto> ingredients)?  $default,) {final _that = this;
switch (_that) {
case _RecipeDto() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.mediaUrl,_that.defaultServings,_that.estimatedCookingMinutes,_that.estimatedCost,_that.servings,_that.instructions,_that.nutrition,_that.ingredients);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RecipeDto extends RecipeDto {
  const _RecipeDto({required this.id, required this.name, this.description = '', @JsonKey(name: 'media_url') this.mediaUrl, @JsonKey(name: 'default_servings', fromJson: _asDouble) this.defaultServings, @JsonKey(name: 'estimated_cooking_minutes') this.estimatedCookingMinutes = 0, @JsonKey(name: 'estimated_cost', fromJson: _asDouble) this.estimatedCost, @JsonKey(fromJson: _asDouble) this.servings, final  Map<String, dynamic>? instructions, this.nutrition, final  List<RecipeIngredientDto> ingredients = const <RecipeIngredientDto>[]}): _instructions = instructions,_ingredients = ingredients,super._();
  factory _RecipeDto.fromJson(Map<String, dynamic> json) => _$RecipeDtoFromJson(json);

@override final  String id;
@override final  String name;
@override@JsonKey() final  String description;
@override@JsonKey(name: 'media_url') final  String? mediaUrl;
@override@JsonKey(name: 'default_servings', fromJson: _asDouble) final  double? defaultServings;
@override@JsonKey(name: 'estimated_cooking_minutes') final  int estimatedCookingMinutes;
@override@JsonKey(name: 'estimated_cost', fromJson: _asDouble) final  double? estimatedCost;
// Detail-only fields (absent on the list endpoint).
@override@JsonKey(fromJson: _asDouble) final  double? servings;
 final  Map<String, dynamic>? _instructions;
@override Map<String, dynamic>? get instructions {
  final value = _instructions;
  if (value == null) return null;
  if (_instructions is EqualUnmodifiableMapView) return _instructions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  RecipeNutritionDto? nutrition;
 final  List<RecipeIngredientDto> _ingredients;
@override@JsonKey() List<RecipeIngredientDto> get ingredients {
  if (_ingredients is EqualUnmodifiableListView) return _ingredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_ingredients);
}


/// Create a copy of RecipeDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RecipeDtoCopyWith<_RecipeDto> get copyWith => __$RecipeDtoCopyWithImpl<_RecipeDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RecipeDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RecipeDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.mediaUrl, mediaUrl) || other.mediaUrl == mediaUrl)&&(identical(other.defaultServings, defaultServings) || other.defaultServings == defaultServings)&&(identical(other.estimatedCookingMinutes, estimatedCookingMinutes) || other.estimatedCookingMinutes == estimatedCookingMinutes)&&(identical(other.estimatedCost, estimatedCost) || other.estimatedCost == estimatedCost)&&(identical(other.servings, servings) || other.servings == servings)&&const DeepCollectionEquality().equals(other._instructions, _instructions)&&(identical(other.nutrition, nutrition) || other.nutrition == nutrition)&&const DeepCollectionEquality().equals(other._ingredients, _ingredients));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,mediaUrl,defaultServings,estimatedCookingMinutes,estimatedCost,servings,const DeepCollectionEquality().hash(_instructions),nutrition,const DeepCollectionEquality().hash(_ingredients));

@override
String toString() {
  return 'RecipeDto(id: $id, name: $name, description: $description, mediaUrl: $mediaUrl, defaultServings: $defaultServings, estimatedCookingMinutes: $estimatedCookingMinutes, estimatedCost: $estimatedCost, servings: $servings, instructions: $instructions, nutrition: $nutrition, ingredients: $ingredients)';
}


}

/// @nodoc
abstract mixin class _$RecipeDtoCopyWith<$Res> implements $RecipeDtoCopyWith<$Res> {
  factory _$RecipeDtoCopyWith(_RecipeDto value, $Res Function(_RecipeDto) _then) = __$RecipeDtoCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String description,@JsonKey(name: 'media_url') String? mediaUrl,@JsonKey(name: 'default_servings', fromJson: _asDouble) double? defaultServings,@JsonKey(name: 'estimated_cooking_minutes') int estimatedCookingMinutes,@JsonKey(name: 'estimated_cost', fromJson: _asDouble) double? estimatedCost,@JsonKey(fromJson: _asDouble) double? servings, Map<String, dynamic>? instructions, RecipeNutritionDto? nutrition, List<RecipeIngredientDto> ingredients
});


@override $RecipeNutritionDtoCopyWith<$Res>? get nutrition;

}
/// @nodoc
class __$RecipeDtoCopyWithImpl<$Res>
    implements _$RecipeDtoCopyWith<$Res> {
  __$RecipeDtoCopyWithImpl(this._self, this._then);

  final _RecipeDto _self;
  final $Res Function(_RecipeDto) _then;

/// Create a copy of RecipeDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = null,Object? mediaUrl = freezed,Object? defaultServings = freezed,Object? estimatedCookingMinutes = null,Object? estimatedCost = freezed,Object? servings = freezed,Object? instructions = freezed,Object? nutrition = freezed,Object? ingredients = null,}) {
  return _then(_RecipeDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,mediaUrl: freezed == mediaUrl ? _self.mediaUrl : mediaUrl // ignore: cast_nullable_to_non_nullable
as String?,defaultServings: freezed == defaultServings ? _self.defaultServings : defaultServings // ignore: cast_nullable_to_non_nullable
as double?,estimatedCookingMinutes: null == estimatedCookingMinutes ? _self.estimatedCookingMinutes : estimatedCookingMinutes // ignore: cast_nullable_to_non_nullable
as int,estimatedCost: freezed == estimatedCost ? _self.estimatedCost : estimatedCost // ignore: cast_nullable_to_non_nullable
as double?,servings: freezed == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double?,instructions: freezed == instructions ? _self._instructions : instructions // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,nutrition: freezed == nutrition ? _self.nutrition : nutrition // ignore: cast_nullable_to_non_nullable
as RecipeNutritionDto?,ingredients: null == ingredients ? _self._ingredients : ingredients // ignore: cast_nullable_to_non_nullable
as List<RecipeIngredientDto>,
  ));
}

/// Create a copy of RecipeDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RecipeNutritionDtoCopyWith<$Res>? get nutrition {
    if (_self.nutrition == null) {
    return null;
  }

  return $RecipeNutritionDtoCopyWith<$Res>(_self.nutrition!, (value) {
    return _then(_self.copyWith(nutrition: value));
  });
}
}


/// @nodoc
mixin _$RecipeNutritionDto {

@JsonKey(fromJson: _asDouble) double? get calories;@JsonKey(name: 'protein_g', fromJson: _asDouble) double? get proteinG;@JsonKey(name: 'fat_g', fromJson: _asDouble) double? get fatG;@JsonKey(name: 'carbs_g', fromJson: _asDouble) double? get carbsG;@JsonKey(name: 'sugar_g', fromJson: _asDouble) double? get sugarG;
/// Create a copy of RecipeNutritionDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecipeNutritionDtoCopyWith<RecipeNutritionDto> get copyWith => _$RecipeNutritionDtoCopyWithImpl<RecipeNutritionDto>(this as RecipeNutritionDto, _$identity);

  /// Serializes this RecipeNutritionDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RecipeNutritionDto&&(identical(other.calories, calories) || other.calories == calories)&&(identical(other.proteinG, proteinG) || other.proteinG == proteinG)&&(identical(other.fatG, fatG) || other.fatG == fatG)&&(identical(other.carbsG, carbsG) || other.carbsG == carbsG)&&(identical(other.sugarG, sugarG) || other.sugarG == sugarG));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,calories,proteinG,fatG,carbsG,sugarG);

@override
String toString() {
  return 'RecipeNutritionDto(calories: $calories, proteinG: $proteinG, fatG: $fatG, carbsG: $carbsG, sugarG: $sugarG)';
}


}

/// @nodoc
abstract mixin class $RecipeNutritionDtoCopyWith<$Res>  {
  factory $RecipeNutritionDtoCopyWith(RecipeNutritionDto value, $Res Function(RecipeNutritionDto) _then) = _$RecipeNutritionDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(fromJson: _asDouble) double? calories,@JsonKey(name: 'protein_g', fromJson: _asDouble) double? proteinG,@JsonKey(name: 'fat_g', fromJson: _asDouble) double? fatG,@JsonKey(name: 'carbs_g', fromJson: _asDouble) double? carbsG,@JsonKey(name: 'sugar_g', fromJson: _asDouble) double? sugarG
});




}
/// @nodoc
class _$RecipeNutritionDtoCopyWithImpl<$Res>
    implements $RecipeNutritionDtoCopyWith<$Res> {
  _$RecipeNutritionDtoCopyWithImpl(this._self, this._then);

  final RecipeNutritionDto _self;
  final $Res Function(RecipeNutritionDto) _then;

/// Create a copy of RecipeNutritionDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? calories = freezed,Object? proteinG = freezed,Object? fatG = freezed,Object? carbsG = freezed,Object? sugarG = freezed,}) {
  return _then(_self.copyWith(
calories: freezed == calories ? _self.calories : calories // ignore: cast_nullable_to_non_nullable
as double?,proteinG: freezed == proteinG ? _self.proteinG : proteinG // ignore: cast_nullable_to_non_nullable
as double?,fatG: freezed == fatG ? _self.fatG : fatG // ignore: cast_nullable_to_non_nullable
as double?,carbsG: freezed == carbsG ? _self.carbsG : carbsG // ignore: cast_nullable_to_non_nullable
as double?,sugarG: freezed == sugarG ? _self.sugarG : sugarG // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}

}


/// Adds pattern-matching-related methods to [RecipeNutritionDto].
extension RecipeNutritionDtoPatterns on RecipeNutritionDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RecipeNutritionDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RecipeNutritionDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RecipeNutritionDto value)  $default,){
final _that = this;
switch (_that) {
case _RecipeNutritionDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RecipeNutritionDto value)?  $default,){
final _that = this;
switch (_that) {
case _RecipeNutritionDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(fromJson: _asDouble)  double? calories, @JsonKey(name: 'protein_g', fromJson: _asDouble)  double? proteinG, @JsonKey(name: 'fat_g', fromJson: _asDouble)  double? fatG, @JsonKey(name: 'carbs_g', fromJson: _asDouble)  double? carbsG, @JsonKey(name: 'sugar_g', fromJson: _asDouble)  double? sugarG)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RecipeNutritionDto() when $default != null:
return $default(_that.calories,_that.proteinG,_that.fatG,_that.carbsG,_that.sugarG);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(fromJson: _asDouble)  double? calories, @JsonKey(name: 'protein_g', fromJson: _asDouble)  double? proteinG, @JsonKey(name: 'fat_g', fromJson: _asDouble)  double? fatG, @JsonKey(name: 'carbs_g', fromJson: _asDouble)  double? carbsG, @JsonKey(name: 'sugar_g', fromJson: _asDouble)  double? sugarG)  $default,) {final _that = this;
switch (_that) {
case _RecipeNutritionDto():
return $default(_that.calories,_that.proteinG,_that.fatG,_that.carbsG,_that.sugarG);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(fromJson: _asDouble)  double? calories, @JsonKey(name: 'protein_g', fromJson: _asDouble)  double? proteinG, @JsonKey(name: 'fat_g', fromJson: _asDouble)  double? fatG, @JsonKey(name: 'carbs_g', fromJson: _asDouble)  double? carbsG, @JsonKey(name: 'sugar_g', fromJson: _asDouble)  double? sugarG)?  $default,) {final _that = this;
switch (_that) {
case _RecipeNutritionDto() when $default != null:
return $default(_that.calories,_that.proteinG,_that.fatG,_that.carbsG,_that.sugarG);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RecipeNutritionDto implements RecipeNutritionDto {
  const _RecipeNutritionDto({@JsonKey(fromJson: _asDouble) this.calories, @JsonKey(name: 'protein_g', fromJson: _asDouble) this.proteinG, @JsonKey(name: 'fat_g', fromJson: _asDouble) this.fatG, @JsonKey(name: 'carbs_g', fromJson: _asDouble) this.carbsG, @JsonKey(name: 'sugar_g', fromJson: _asDouble) this.sugarG});
  factory _RecipeNutritionDto.fromJson(Map<String, dynamic> json) => _$RecipeNutritionDtoFromJson(json);

@override@JsonKey(fromJson: _asDouble) final  double? calories;
@override@JsonKey(name: 'protein_g', fromJson: _asDouble) final  double? proteinG;
@override@JsonKey(name: 'fat_g', fromJson: _asDouble) final  double? fatG;
@override@JsonKey(name: 'carbs_g', fromJson: _asDouble) final  double? carbsG;
@override@JsonKey(name: 'sugar_g', fromJson: _asDouble) final  double? sugarG;

/// Create a copy of RecipeNutritionDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RecipeNutritionDtoCopyWith<_RecipeNutritionDto> get copyWith => __$RecipeNutritionDtoCopyWithImpl<_RecipeNutritionDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RecipeNutritionDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RecipeNutritionDto&&(identical(other.calories, calories) || other.calories == calories)&&(identical(other.proteinG, proteinG) || other.proteinG == proteinG)&&(identical(other.fatG, fatG) || other.fatG == fatG)&&(identical(other.carbsG, carbsG) || other.carbsG == carbsG)&&(identical(other.sugarG, sugarG) || other.sugarG == sugarG));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,calories,proteinG,fatG,carbsG,sugarG);

@override
String toString() {
  return 'RecipeNutritionDto(calories: $calories, proteinG: $proteinG, fatG: $fatG, carbsG: $carbsG, sugarG: $sugarG)';
}


}

/// @nodoc
abstract mixin class _$RecipeNutritionDtoCopyWith<$Res> implements $RecipeNutritionDtoCopyWith<$Res> {
  factory _$RecipeNutritionDtoCopyWith(_RecipeNutritionDto value, $Res Function(_RecipeNutritionDto) _then) = __$RecipeNutritionDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(fromJson: _asDouble) double? calories,@JsonKey(name: 'protein_g', fromJson: _asDouble) double? proteinG,@JsonKey(name: 'fat_g', fromJson: _asDouble) double? fatG,@JsonKey(name: 'carbs_g', fromJson: _asDouble) double? carbsG,@JsonKey(name: 'sugar_g', fromJson: _asDouble) double? sugarG
});




}
/// @nodoc
class __$RecipeNutritionDtoCopyWithImpl<$Res>
    implements _$RecipeNutritionDtoCopyWith<$Res> {
  __$RecipeNutritionDtoCopyWithImpl(this._self, this._then);

  final _RecipeNutritionDto _self;
  final $Res Function(_RecipeNutritionDto) _then;

/// Create a copy of RecipeNutritionDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? calories = freezed,Object? proteinG = freezed,Object? fatG = freezed,Object? carbsG = freezed,Object? sugarG = freezed,}) {
  return _then(_RecipeNutritionDto(
calories: freezed == calories ? _self.calories : calories // ignore: cast_nullable_to_non_nullable
as double?,proteinG: freezed == proteinG ? _self.proteinG : proteinG // ignore: cast_nullable_to_non_nullable
as double?,fatG: freezed == fatG ? _self.fatG : fatG // ignore: cast_nullable_to_non_nullable
as double?,carbsG: freezed == carbsG ? _self.carbsG : carbsG // ignore: cast_nullable_to_non_nullable
as double?,sugarG: freezed == sugarG ? _self.sugarG : sugarG // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}


}


/// @nodoc
mixin _$RecipeIngredientDto {

@JsonKey(name: 'recipe_ingredient_id') String? get recipeIngredientId;@JsonKey(name: 'master_ingredient_id') String? get masterIngredientId; String get name;@JsonKey(name: 'required_quantity', fromJson: _asDouble) double? get requiredQuantity; String get unit;@JsonKey(name: 'is_optional') bool get isOptional;@JsonKey(name: 'preparation_note') String? get preparationNote;
/// Create a copy of RecipeIngredientDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecipeIngredientDtoCopyWith<RecipeIngredientDto> get copyWith => _$RecipeIngredientDtoCopyWithImpl<RecipeIngredientDto>(this as RecipeIngredientDto, _$identity);

  /// Serializes this RecipeIngredientDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RecipeIngredientDto&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId)&&(identical(other.name, name) || other.name == name)&&(identical(other.requiredQuantity, requiredQuantity) || other.requiredQuantity == requiredQuantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.isOptional, isOptional) || other.isOptional == isOptional)&&(identical(other.preparationNote, preparationNote) || other.preparationNote == preparationNote));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,masterIngredientId,name,requiredQuantity,unit,isOptional,preparationNote);

@override
String toString() {
  return 'RecipeIngredientDto(recipeIngredientId: $recipeIngredientId, masterIngredientId: $masterIngredientId, name: $name, requiredQuantity: $requiredQuantity, unit: $unit, isOptional: $isOptional, preparationNote: $preparationNote)';
}


}

/// @nodoc
abstract mixin class $RecipeIngredientDtoCopyWith<$Res>  {
  factory $RecipeIngredientDtoCopyWith(RecipeIngredientDto value, $Res Function(RecipeIngredientDto) _then) = _$RecipeIngredientDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'recipe_ingredient_id') String? recipeIngredientId,@JsonKey(name: 'master_ingredient_id') String? masterIngredientId, String name,@JsonKey(name: 'required_quantity', fromJson: _asDouble) double? requiredQuantity, String unit,@JsonKey(name: 'is_optional') bool isOptional,@JsonKey(name: 'preparation_note') String? preparationNote
});




}
/// @nodoc
class _$RecipeIngredientDtoCopyWithImpl<$Res>
    implements $RecipeIngredientDtoCopyWith<$Res> {
  _$RecipeIngredientDtoCopyWithImpl(this._self, this._then);

  final RecipeIngredientDto _self;
  final $Res Function(RecipeIngredientDto) _then;

/// Create a copy of RecipeIngredientDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeIngredientId = freezed,Object? masterIngredientId = freezed,Object? name = null,Object? requiredQuantity = freezed,Object? unit = null,Object? isOptional = null,Object? preparationNote = freezed,}) {
  return _then(_self.copyWith(
recipeIngredientId: freezed == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String?,masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,requiredQuantity: freezed == requiredQuantity ? _self.requiredQuantity : requiredQuantity // ignore: cast_nullable_to_non_nullable
as double?,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,isOptional: null == isOptional ? _self.isOptional : isOptional // ignore: cast_nullable_to_non_nullable
as bool,preparationNote: freezed == preparationNote ? _self.preparationNote : preparationNote // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [RecipeIngredientDto].
extension RecipeIngredientDtoPatterns on RecipeIngredientDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RecipeIngredientDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RecipeIngredientDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RecipeIngredientDto value)  $default,){
final _that = this;
switch (_that) {
case _RecipeIngredientDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RecipeIngredientDto value)?  $default,){
final _that = this;
switch (_that) {
case _RecipeIngredientDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_ingredient_id')  String? recipeIngredientId, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId,  String name, @JsonKey(name: 'required_quantity', fromJson: _asDouble)  double? requiredQuantity,  String unit, @JsonKey(name: 'is_optional')  bool isOptional, @JsonKey(name: 'preparation_note')  String? preparationNote)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RecipeIngredientDto() when $default != null:
return $default(_that.recipeIngredientId,_that.masterIngredientId,_that.name,_that.requiredQuantity,_that.unit,_that.isOptional,_that.preparationNote);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_ingredient_id')  String? recipeIngredientId, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId,  String name, @JsonKey(name: 'required_quantity', fromJson: _asDouble)  double? requiredQuantity,  String unit, @JsonKey(name: 'is_optional')  bool isOptional, @JsonKey(name: 'preparation_note')  String? preparationNote)  $default,) {final _that = this;
switch (_that) {
case _RecipeIngredientDto():
return $default(_that.recipeIngredientId,_that.masterIngredientId,_that.name,_that.requiredQuantity,_that.unit,_that.isOptional,_that.preparationNote);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'recipe_ingredient_id')  String? recipeIngredientId, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId,  String name, @JsonKey(name: 'required_quantity', fromJson: _asDouble)  double? requiredQuantity,  String unit, @JsonKey(name: 'is_optional')  bool isOptional, @JsonKey(name: 'preparation_note')  String? preparationNote)?  $default,) {final _that = this;
switch (_that) {
case _RecipeIngredientDto() when $default != null:
return $default(_that.recipeIngredientId,_that.masterIngredientId,_that.name,_that.requiredQuantity,_that.unit,_that.isOptional,_that.preparationNote);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RecipeIngredientDto extends RecipeIngredientDto {
  const _RecipeIngredientDto({@JsonKey(name: 'recipe_ingredient_id') this.recipeIngredientId, @JsonKey(name: 'master_ingredient_id') this.masterIngredientId, this.name = '', @JsonKey(name: 'required_quantity', fromJson: _asDouble) this.requiredQuantity, this.unit = 'GRAM', @JsonKey(name: 'is_optional') this.isOptional = false, @JsonKey(name: 'preparation_note') this.preparationNote}): super._();
  factory _RecipeIngredientDto.fromJson(Map<String, dynamic> json) => _$RecipeIngredientDtoFromJson(json);

@override@JsonKey(name: 'recipe_ingredient_id') final  String? recipeIngredientId;
@override@JsonKey(name: 'master_ingredient_id') final  String? masterIngredientId;
@override@JsonKey() final  String name;
@override@JsonKey(name: 'required_quantity', fromJson: _asDouble) final  double? requiredQuantity;
@override@JsonKey() final  String unit;
@override@JsonKey(name: 'is_optional') final  bool isOptional;
@override@JsonKey(name: 'preparation_note') final  String? preparationNote;

/// Create a copy of RecipeIngredientDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RecipeIngredientDtoCopyWith<_RecipeIngredientDto> get copyWith => __$RecipeIngredientDtoCopyWithImpl<_RecipeIngredientDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RecipeIngredientDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RecipeIngredientDto&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId)&&(identical(other.name, name) || other.name == name)&&(identical(other.requiredQuantity, requiredQuantity) || other.requiredQuantity == requiredQuantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.isOptional, isOptional) || other.isOptional == isOptional)&&(identical(other.preparationNote, preparationNote) || other.preparationNote == preparationNote));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,masterIngredientId,name,requiredQuantity,unit,isOptional,preparationNote);

@override
String toString() {
  return 'RecipeIngredientDto(recipeIngredientId: $recipeIngredientId, masterIngredientId: $masterIngredientId, name: $name, requiredQuantity: $requiredQuantity, unit: $unit, isOptional: $isOptional, preparationNote: $preparationNote)';
}


}

/// @nodoc
abstract mixin class _$RecipeIngredientDtoCopyWith<$Res> implements $RecipeIngredientDtoCopyWith<$Res> {
  factory _$RecipeIngredientDtoCopyWith(_RecipeIngredientDto value, $Res Function(_RecipeIngredientDto) _then) = __$RecipeIngredientDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'recipe_ingredient_id') String? recipeIngredientId,@JsonKey(name: 'master_ingredient_id') String? masterIngredientId, String name,@JsonKey(name: 'required_quantity', fromJson: _asDouble) double? requiredQuantity, String unit,@JsonKey(name: 'is_optional') bool isOptional,@JsonKey(name: 'preparation_note') String? preparationNote
});




}
/// @nodoc
class __$RecipeIngredientDtoCopyWithImpl<$Res>
    implements _$RecipeIngredientDtoCopyWith<$Res> {
  __$RecipeIngredientDtoCopyWithImpl(this._self, this._then);

  final _RecipeIngredientDto _self;
  final $Res Function(_RecipeIngredientDto) _then;

/// Create a copy of RecipeIngredientDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeIngredientId = freezed,Object? masterIngredientId = freezed,Object? name = null,Object? requiredQuantity = freezed,Object? unit = null,Object? isOptional = null,Object? preparationNote = freezed,}) {
  return _then(_RecipeIngredientDto(
recipeIngredientId: freezed == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String?,masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,requiredQuantity: freezed == requiredQuantity ? _self.requiredQuantity : requiredQuantity // ignore: cast_nullable_to_non_nullable
as double?,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,isOptional: null == isOptional ? _self.isOptional : isOptional // ignore: cast_nullable_to_non_nullable
as bool,preparationNote: freezed == preparationNote ? _self.preparationNote : preparationNote // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
