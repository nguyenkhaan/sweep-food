// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ingredient_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$IngredientDto {

 String get id; String get name; IngredientCategoryDto get category;@JsonKey(name: 'default_unit') String get defaultUnit;@JsonKey(name: 'default_storage_mode') String? get defaultStorageMode; List<String> get aliases; String? get description; IngredientNutritionDto? get nutrition;@JsonKey(name: 'shelf_life_rules') List<ShelfLifeRuleDto> get shelfLifeRules;
/// Create a copy of IngredientDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$IngredientDtoCopyWith<IngredientDto> get copyWith => _$IngredientDtoCopyWithImpl<IngredientDto>(this as IngredientDto, _$identity);

  /// Serializes this IngredientDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is IngredientDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.defaultUnit, defaultUnit) || other.defaultUnit == defaultUnit)&&(identical(other.defaultStorageMode, defaultStorageMode) || other.defaultStorageMode == defaultStorageMode)&&const DeepCollectionEquality().equals(other.aliases, aliases)&&(identical(other.description, description) || other.description == description)&&(identical(other.nutrition, nutrition) || other.nutrition == nutrition)&&const DeepCollectionEquality().equals(other.shelfLifeRules, shelfLifeRules));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,category,defaultUnit,defaultStorageMode,const DeepCollectionEquality().hash(aliases),description,nutrition,const DeepCollectionEquality().hash(shelfLifeRules));

@override
String toString() {
  return 'IngredientDto(id: $id, name: $name, category: $category, defaultUnit: $defaultUnit, defaultStorageMode: $defaultStorageMode, aliases: $aliases, description: $description, nutrition: $nutrition, shelfLifeRules: $shelfLifeRules)';
}


}

/// @nodoc
abstract mixin class $IngredientDtoCopyWith<$Res>  {
  factory $IngredientDtoCopyWith(IngredientDto value, $Res Function(IngredientDto) _then) = _$IngredientDtoCopyWithImpl;
@useResult
$Res call({
 String id, String name, IngredientCategoryDto category,@JsonKey(name: 'default_unit') String defaultUnit,@JsonKey(name: 'default_storage_mode') String? defaultStorageMode, List<String> aliases, String? description, IngredientNutritionDto? nutrition,@JsonKey(name: 'shelf_life_rules') List<ShelfLifeRuleDto> shelfLifeRules
});


$IngredientCategoryDtoCopyWith<$Res> get category;$IngredientNutritionDtoCopyWith<$Res>? get nutrition;

}
/// @nodoc
class _$IngredientDtoCopyWithImpl<$Res>
    implements $IngredientDtoCopyWith<$Res> {
  _$IngredientDtoCopyWithImpl(this._self, this._then);

  final IngredientDto _self;
  final $Res Function(IngredientDto) _then;

/// Create a copy of IngredientDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? category = null,Object? defaultUnit = null,Object? defaultStorageMode = freezed,Object? aliases = null,Object? description = freezed,Object? nutrition = freezed,Object? shelfLifeRules = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as IngredientCategoryDto,defaultUnit: null == defaultUnit ? _self.defaultUnit : defaultUnit // ignore: cast_nullable_to_non_nullable
as String,defaultStorageMode: freezed == defaultStorageMode ? _self.defaultStorageMode : defaultStorageMode // ignore: cast_nullable_to_non_nullable
as String?,aliases: null == aliases ? _self.aliases : aliases // ignore: cast_nullable_to_non_nullable
as List<String>,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,nutrition: freezed == nutrition ? _self.nutrition : nutrition // ignore: cast_nullable_to_non_nullable
as IngredientNutritionDto?,shelfLifeRules: null == shelfLifeRules ? _self.shelfLifeRules : shelfLifeRules // ignore: cast_nullable_to_non_nullable
as List<ShelfLifeRuleDto>,
  ));
}
/// Create a copy of IngredientDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IngredientCategoryDtoCopyWith<$Res> get category {
  
  return $IngredientCategoryDtoCopyWith<$Res>(_self.category, (value) {
    return _then(_self.copyWith(category: value));
  });
}/// Create a copy of IngredientDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IngredientNutritionDtoCopyWith<$Res>? get nutrition {
    if (_self.nutrition == null) {
    return null;
  }

  return $IngredientNutritionDtoCopyWith<$Res>(_self.nutrition!, (value) {
    return _then(_self.copyWith(nutrition: value));
  });
}
}


/// Adds pattern-matching-related methods to [IngredientDto].
extension IngredientDtoPatterns on IngredientDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _IngredientDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _IngredientDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _IngredientDto value)  $default,){
final _that = this;
switch (_that) {
case _IngredientDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _IngredientDto value)?  $default,){
final _that = this;
switch (_that) {
case _IngredientDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  IngredientCategoryDto category, @JsonKey(name: 'default_unit')  String defaultUnit, @JsonKey(name: 'default_storage_mode')  String? defaultStorageMode,  List<String> aliases,  String? description,  IngredientNutritionDto? nutrition, @JsonKey(name: 'shelf_life_rules')  List<ShelfLifeRuleDto> shelfLifeRules)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _IngredientDto() when $default != null:
return $default(_that.id,_that.name,_that.category,_that.defaultUnit,_that.defaultStorageMode,_that.aliases,_that.description,_that.nutrition,_that.shelfLifeRules);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  IngredientCategoryDto category, @JsonKey(name: 'default_unit')  String defaultUnit, @JsonKey(name: 'default_storage_mode')  String? defaultStorageMode,  List<String> aliases,  String? description,  IngredientNutritionDto? nutrition, @JsonKey(name: 'shelf_life_rules')  List<ShelfLifeRuleDto> shelfLifeRules)  $default,) {final _that = this;
switch (_that) {
case _IngredientDto():
return $default(_that.id,_that.name,_that.category,_that.defaultUnit,_that.defaultStorageMode,_that.aliases,_that.description,_that.nutrition,_that.shelfLifeRules);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  IngredientCategoryDto category, @JsonKey(name: 'default_unit')  String defaultUnit, @JsonKey(name: 'default_storage_mode')  String? defaultStorageMode,  List<String> aliases,  String? description,  IngredientNutritionDto? nutrition, @JsonKey(name: 'shelf_life_rules')  List<ShelfLifeRuleDto> shelfLifeRules)?  $default,) {final _that = this;
switch (_that) {
case _IngredientDto() when $default != null:
return $default(_that.id,_that.name,_that.category,_that.defaultUnit,_that.defaultStorageMode,_that.aliases,_that.description,_that.nutrition,_that.shelfLifeRules);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _IngredientDto extends IngredientDto {
  const _IngredientDto({required this.id, required this.name, required this.category, @JsonKey(name: 'default_unit') this.defaultUnit = 'GRAM', @JsonKey(name: 'default_storage_mode') this.defaultStorageMode, final  List<String> aliases = const <String>[], this.description, this.nutrition, @JsonKey(name: 'shelf_life_rules') final  List<ShelfLifeRuleDto> shelfLifeRules = const <ShelfLifeRuleDto>[]}): _aliases = aliases,_shelfLifeRules = shelfLifeRules,super._();
  factory _IngredientDto.fromJson(Map<String, dynamic> json) => _$IngredientDtoFromJson(json);

@override final  String id;
@override final  String name;
@override final  IngredientCategoryDto category;
@override@JsonKey(name: 'default_unit') final  String defaultUnit;
@override@JsonKey(name: 'default_storage_mode') final  String? defaultStorageMode;
 final  List<String> _aliases;
@override@JsonKey() List<String> get aliases {
  if (_aliases is EqualUnmodifiableListView) return _aliases;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_aliases);
}

@override final  String? description;
@override final  IngredientNutritionDto? nutrition;
 final  List<ShelfLifeRuleDto> _shelfLifeRules;
@override@JsonKey(name: 'shelf_life_rules') List<ShelfLifeRuleDto> get shelfLifeRules {
  if (_shelfLifeRules is EqualUnmodifiableListView) return _shelfLifeRules;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_shelfLifeRules);
}


/// Create a copy of IngredientDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$IngredientDtoCopyWith<_IngredientDto> get copyWith => __$IngredientDtoCopyWithImpl<_IngredientDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$IngredientDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _IngredientDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.defaultUnit, defaultUnit) || other.defaultUnit == defaultUnit)&&(identical(other.defaultStorageMode, defaultStorageMode) || other.defaultStorageMode == defaultStorageMode)&&const DeepCollectionEquality().equals(other._aliases, _aliases)&&(identical(other.description, description) || other.description == description)&&(identical(other.nutrition, nutrition) || other.nutrition == nutrition)&&const DeepCollectionEquality().equals(other._shelfLifeRules, _shelfLifeRules));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,category,defaultUnit,defaultStorageMode,const DeepCollectionEquality().hash(_aliases),description,nutrition,const DeepCollectionEquality().hash(_shelfLifeRules));

@override
String toString() {
  return 'IngredientDto(id: $id, name: $name, category: $category, defaultUnit: $defaultUnit, defaultStorageMode: $defaultStorageMode, aliases: $aliases, description: $description, nutrition: $nutrition, shelfLifeRules: $shelfLifeRules)';
}


}

/// @nodoc
abstract mixin class _$IngredientDtoCopyWith<$Res> implements $IngredientDtoCopyWith<$Res> {
  factory _$IngredientDtoCopyWith(_IngredientDto value, $Res Function(_IngredientDto) _then) = __$IngredientDtoCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, IngredientCategoryDto category,@JsonKey(name: 'default_unit') String defaultUnit,@JsonKey(name: 'default_storage_mode') String? defaultStorageMode, List<String> aliases, String? description, IngredientNutritionDto? nutrition,@JsonKey(name: 'shelf_life_rules') List<ShelfLifeRuleDto> shelfLifeRules
});


@override $IngredientCategoryDtoCopyWith<$Res> get category;@override $IngredientNutritionDtoCopyWith<$Res>? get nutrition;

}
/// @nodoc
class __$IngredientDtoCopyWithImpl<$Res>
    implements _$IngredientDtoCopyWith<$Res> {
  __$IngredientDtoCopyWithImpl(this._self, this._then);

  final _IngredientDto _self;
  final $Res Function(_IngredientDto) _then;

/// Create a copy of IngredientDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? category = null,Object? defaultUnit = null,Object? defaultStorageMode = freezed,Object? aliases = null,Object? description = freezed,Object? nutrition = freezed,Object? shelfLifeRules = null,}) {
  return _then(_IngredientDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as IngredientCategoryDto,defaultUnit: null == defaultUnit ? _self.defaultUnit : defaultUnit // ignore: cast_nullable_to_non_nullable
as String,defaultStorageMode: freezed == defaultStorageMode ? _self.defaultStorageMode : defaultStorageMode // ignore: cast_nullable_to_non_nullable
as String?,aliases: null == aliases ? _self._aliases : aliases // ignore: cast_nullable_to_non_nullable
as List<String>,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,nutrition: freezed == nutrition ? _self.nutrition : nutrition // ignore: cast_nullable_to_non_nullable
as IngredientNutritionDto?,shelfLifeRules: null == shelfLifeRules ? _self._shelfLifeRules : shelfLifeRules // ignore: cast_nullable_to_non_nullable
as List<ShelfLifeRuleDto>,
  ));
}

/// Create a copy of IngredientDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IngredientCategoryDtoCopyWith<$Res> get category {
  
  return $IngredientCategoryDtoCopyWith<$Res>(_self.category, (value) {
    return _then(_self.copyWith(category: value));
  });
}/// Create a copy of IngredientDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IngredientNutritionDtoCopyWith<$Res>? get nutrition {
    if (_self.nutrition == null) {
    return null;
  }

  return $IngredientNutritionDtoCopyWith<$Res>(_self.nutrition!, (value) {
    return _then(_self.copyWith(nutrition: value));
  });
}
}


/// @nodoc
mixin _$IngredientCategoryDto {

 String get id; String get name;
/// Create a copy of IngredientCategoryDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$IngredientCategoryDtoCopyWith<IngredientCategoryDto> get copyWith => _$IngredientCategoryDtoCopyWithImpl<IngredientCategoryDto>(this as IngredientCategoryDto, _$identity);

  /// Serializes this IngredientCategoryDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is IngredientCategoryDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name);

@override
String toString() {
  return 'IngredientCategoryDto(id: $id, name: $name)';
}


}

/// @nodoc
abstract mixin class $IngredientCategoryDtoCopyWith<$Res>  {
  factory $IngredientCategoryDtoCopyWith(IngredientCategoryDto value, $Res Function(IngredientCategoryDto) _then) = _$IngredientCategoryDtoCopyWithImpl;
@useResult
$Res call({
 String id, String name
});




}
/// @nodoc
class _$IngredientCategoryDtoCopyWithImpl<$Res>
    implements $IngredientCategoryDtoCopyWith<$Res> {
  _$IngredientCategoryDtoCopyWithImpl(this._self, this._then);

  final IngredientCategoryDto _self;
  final $Res Function(IngredientCategoryDto) _then;

/// Create a copy of IngredientCategoryDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [IngredientCategoryDto].
extension IngredientCategoryDtoPatterns on IngredientCategoryDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _IngredientCategoryDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _IngredientCategoryDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _IngredientCategoryDto value)  $default,){
final _that = this;
switch (_that) {
case _IngredientCategoryDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _IngredientCategoryDto value)?  $default,){
final _that = this;
switch (_that) {
case _IngredientCategoryDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _IngredientCategoryDto() when $default != null:
return $default(_that.id,_that.name);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name)  $default,) {final _that = this;
switch (_that) {
case _IngredientCategoryDto():
return $default(_that.id,_that.name);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name)?  $default,) {final _that = this;
switch (_that) {
case _IngredientCategoryDto() when $default != null:
return $default(_that.id,_that.name);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _IngredientCategoryDto implements IngredientCategoryDto {
  const _IngredientCategoryDto({required this.id, required this.name});
  factory _IngredientCategoryDto.fromJson(Map<String, dynamic> json) => _$IngredientCategoryDtoFromJson(json);

@override final  String id;
@override final  String name;

/// Create a copy of IngredientCategoryDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$IngredientCategoryDtoCopyWith<_IngredientCategoryDto> get copyWith => __$IngredientCategoryDtoCopyWithImpl<_IngredientCategoryDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$IngredientCategoryDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _IngredientCategoryDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name);

@override
String toString() {
  return 'IngredientCategoryDto(id: $id, name: $name)';
}


}

/// @nodoc
abstract mixin class _$IngredientCategoryDtoCopyWith<$Res> implements $IngredientCategoryDtoCopyWith<$Res> {
  factory _$IngredientCategoryDtoCopyWith(_IngredientCategoryDto value, $Res Function(_IngredientCategoryDto) _then) = __$IngredientCategoryDtoCopyWithImpl;
@override @useResult
$Res call({
 String id, String name
});




}
/// @nodoc
class __$IngredientCategoryDtoCopyWithImpl<$Res>
    implements _$IngredientCategoryDtoCopyWith<$Res> {
  __$IngredientCategoryDtoCopyWithImpl(this._self, this._then);

  final _IngredientCategoryDto _self;
  final $Res Function(_IngredientCategoryDto) _then;

/// Create a copy of IngredientCategoryDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,}) {
  return _then(_IngredientCategoryDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$IngredientNutritionDto {

@JsonKey(fromJson: _asDouble) double? get calories;@JsonKey(name: 'protein_g', fromJson: _asDouble) double? get proteinG;@JsonKey(name: 'fat_g', fromJson: _asDouble) double? get fatG;@JsonKey(name: 'carbs_g', fromJson: _asDouble) double? get carbsG;@JsonKey(name: 'sugar_g', fromJson: _asDouble) double? get sugarG;@JsonKey(name: 'sodium_mg', fromJson: _asDouble) double? get sodiumMg;
/// Create a copy of IngredientNutritionDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$IngredientNutritionDtoCopyWith<IngredientNutritionDto> get copyWith => _$IngredientNutritionDtoCopyWithImpl<IngredientNutritionDto>(this as IngredientNutritionDto, _$identity);

  /// Serializes this IngredientNutritionDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is IngredientNutritionDto&&(identical(other.calories, calories) || other.calories == calories)&&(identical(other.proteinG, proteinG) || other.proteinG == proteinG)&&(identical(other.fatG, fatG) || other.fatG == fatG)&&(identical(other.carbsG, carbsG) || other.carbsG == carbsG)&&(identical(other.sugarG, sugarG) || other.sugarG == sugarG)&&(identical(other.sodiumMg, sodiumMg) || other.sodiumMg == sodiumMg));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,calories,proteinG,fatG,carbsG,sugarG,sodiumMg);

@override
String toString() {
  return 'IngredientNutritionDto(calories: $calories, proteinG: $proteinG, fatG: $fatG, carbsG: $carbsG, sugarG: $sugarG, sodiumMg: $sodiumMg)';
}


}

/// @nodoc
abstract mixin class $IngredientNutritionDtoCopyWith<$Res>  {
  factory $IngredientNutritionDtoCopyWith(IngredientNutritionDto value, $Res Function(IngredientNutritionDto) _then) = _$IngredientNutritionDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(fromJson: _asDouble) double? calories,@JsonKey(name: 'protein_g', fromJson: _asDouble) double? proteinG,@JsonKey(name: 'fat_g', fromJson: _asDouble) double? fatG,@JsonKey(name: 'carbs_g', fromJson: _asDouble) double? carbsG,@JsonKey(name: 'sugar_g', fromJson: _asDouble) double? sugarG,@JsonKey(name: 'sodium_mg', fromJson: _asDouble) double? sodiumMg
});




}
/// @nodoc
class _$IngredientNutritionDtoCopyWithImpl<$Res>
    implements $IngredientNutritionDtoCopyWith<$Res> {
  _$IngredientNutritionDtoCopyWithImpl(this._self, this._then);

  final IngredientNutritionDto _self;
  final $Res Function(IngredientNutritionDto) _then;

/// Create a copy of IngredientNutritionDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? calories = freezed,Object? proteinG = freezed,Object? fatG = freezed,Object? carbsG = freezed,Object? sugarG = freezed,Object? sodiumMg = freezed,}) {
  return _then(_self.copyWith(
calories: freezed == calories ? _self.calories : calories // ignore: cast_nullable_to_non_nullable
as double?,proteinG: freezed == proteinG ? _self.proteinG : proteinG // ignore: cast_nullable_to_non_nullable
as double?,fatG: freezed == fatG ? _self.fatG : fatG // ignore: cast_nullable_to_non_nullable
as double?,carbsG: freezed == carbsG ? _self.carbsG : carbsG // ignore: cast_nullable_to_non_nullable
as double?,sugarG: freezed == sugarG ? _self.sugarG : sugarG // ignore: cast_nullable_to_non_nullable
as double?,sodiumMg: freezed == sodiumMg ? _self.sodiumMg : sodiumMg // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}

}


/// Adds pattern-matching-related methods to [IngredientNutritionDto].
extension IngredientNutritionDtoPatterns on IngredientNutritionDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _IngredientNutritionDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _IngredientNutritionDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _IngredientNutritionDto value)  $default,){
final _that = this;
switch (_that) {
case _IngredientNutritionDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _IngredientNutritionDto value)?  $default,){
final _that = this;
switch (_that) {
case _IngredientNutritionDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(fromJson: _asDouble)  double? calories, @JsonKey(name: 'protein_g', fromJson: _asDouble)  double? proteinG, @JsonKey(name: 'fat_g', fromJson: _asDouble)  double? fatG, @JsonKey(name: 'carbs_g', fromJson: _asDouble)  double? carbsG, @JsonKey(name: 'sugar_g', fromJson: _asDouble)  double? sugarG, @JsonKey(name: 'sodium_mg', fromJson: _asDouble)  double? sodiumMg)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _IngredientNutritionDto() when $default != null:
return $default(_that.calories,_that.proteinG,_that.fatG,_that.carbsG,_that.sugarG,_that.sodiumMg);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(fromJson: _asDouble)  double? calories, @JsonKey(name: 'protein_g', fromJson: _asDouble)  double? proteinG, @JsonKey(name: 'fat_g', fromJson: _asDouble)  double? fatG, @JsonKey(name: 'carbs_g', fromJson: _asDouble)  double? carbsG, @JsonKey(name: 'sugar_g', fromJson: _asDouble)  double? sugarG, @JsonKey(name: 'sodium_mg', fromJson: _asDouble)  double? sodiumMg)  $default,) {final _that = this;
switch (_that) {
case _IngredientNutritionDto():
return $default(_that.calories,_that.proteinG,_that.fatG,_that.carbsG,_that.sugarG,_that.sodiumMg);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(fromJson: _asDouble)  double? calories, @JsonKey(name: 'protein_g', fromJson: _asDouble)  double? proteinG, @JsonKey(name: 'fat_g', fromJson: _asDouble)  double? fatG, @JsonKey(name: 'carbs_g', fromJson: _asDouble)  double? carbsG, @JsonKey(name: 'sugar_g', fromJson: _asDouble)  double? sugarG, @JsonKey(name: 'sodium_mg', fromJson: _asDouble)  double? sodiumMg)?  $default,) {final _that = this;
switch (_that) {
case _IngredientNutritionDto() when $default != null:
return $default(_that.calories,_that.proteinG,_that.fatG,_that.carbsG,_that.sugarG,_that.sodiumMg);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _IngredientNutritionDto extends IngredientNutritionDto {
  const _IngredientNutritionDto({@JsonKey(fromJson: _asDouble) this.calories, @JsonKey(name: 'protein_g', fromJson: _asDouble) this.proteinG, @JsonKey(name: 'fat_g', fromJson: _asDouble) this.fatG, @JsonKey(name: 'carbs_g', fromJson: _asDouble) this.carbsG, @JsonKey(name: 'sugar_g', fromJson: _asDouble) this.sugarG, @JsonKey(name: 'sodium_mg', fromJson: _asDouble) this.sodiumMg}): super._();
  factory _IngredientNutritionDto.fromJson(Map<String, dynamic> json) => _$IngredientNutritionDtoFromJson(json);

@override@JsonKey(fromJson: _asDouble) final  double? calories;
@override@JsonKey(name: 'protein_g', fromJson: _asDouble) final  double? proteinG;
@override@JsonKey(name: 'fat_g', fromJson: _asDouble) final  double? fatG;
@override@JsonKey(name: 'carbs_g', fromJson: _asDouble) final  double? carbsG;
@override@JsonKey(name: 'sugar_g', fromJson: _asDouble) final  double? sugarG;
@override@JsonKey(name: 'sodium_mg', fromJson: _asDouble) final  double? sodiumMg;

/// Create a copy of IngredientNutritionDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$IngredientNutritionDtoCopyWith<_IngredientNutritionDto> get copyWith => __$IngredientNutritionDtoCopyWithImpl<_IngredientNutritionDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$IngredientNutritionDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _IngredientNutritionDto&&(identical(other.calories, calories) || other.calories == calories)&&(identical(other.proteinG, proteinG) || other.proteinG == proteinG)&&(identical(other.fatG, fatG) || other.fatG == fatG)&&(identical(other.carbsG, carbsG) || other.carbsG == carbsG)&&(identical(other.sugarG, sugarG) || other.sugarG == sugarG)&&(identical(other.sodiumMg, sodiumMg) || other.sodiumMg == sodiumMg));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,calories,proteinG,fatG,carbsG,sugarG,sodiumMg);

@override
String toString() {
  return 'IngredientNutritionDto(calories: $calories, proteinG: $proteinG, fatG: $fatG, carbsG: $carbsG, sugarG: $sugarG, sodiumMg: $sodiumMg)';
}


}

/// @nodoc
abstract mixin class _$IngredientNutritionDtoCopyWith<$Res> implements $IngredientNutritionDtoCopyWith<$Res> {
  factory _$IngredientNutritionDtoCopyWith(_IngredientNutritionDto value, $Res Function(_IngredientNutritionDto) _then) = __$IngredientNutritionDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(fromJson: _asDouble) double? calories,@JsonKey(name: 'protein_g', fromJson: _asDouble) double? proteinG,@JsonKey(name: 'fat_g', fromJson: _asDouble) double? fatG,@JsonKey(name: 'carbs_g', fromJson: _asDouble) double? carbsG,@JsonKey(name: 'sugar_g', fromJson: _asDouble) double? sugarG,@JsonKey(name: 'sodium_mg', fromJson: _asDouble) double? sodiumMg
});




}
/// @nodoc
class __$IngredientNutritionDtoCopyWithImpl<$Res>
    implements _$IngredientNutritionDtoCopyWith<$Res> {
  __$IngredientNutritionDtoCopyWithImpl(this._self, this._then);

  final _IngredientNutritionDto _self;
  final $Res Function(_IngredientNutritionDto) _then;

/// Create a copy of IngredientNutritionDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? calories = freezed,Object? proteinG = freezed,Object? fatG = freezed,Object? carbsG = freezed,Object? sugarG = freezed,Object? sodiumMg = freezed,}) {
  return _then(_IngredientNutritionDto(
calories: freezed == calories ? _self.calories : calories // ignore: cast_nullable_to_non_nullable
as double?,proteinG: freezed == proteinG ? _self.proteinG : proteinG // ignore: cast_nullable_to_non_nullable
as double?,fatG: freezed == fatG ? _self.fatG : fatG // ignore: cast_nullable_to_non_nullable
as double?,carbsG: freezed == carbsG ? _self.carbsG : carbsG // ignore: cast_nullable_to_non_nullable
as double?,sugarG: freezed == sugarG ? _self.sugarG : sugarG // ignore: cast_nullable_to_non_nullable
as double?,sodiumMg: freezed == sodiumMg ? _self.sodiumMg : sodiumMg // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}


}


/// @nodoc
mixin _$ShelfLifeRuleDto {

 String? get scope;@JsonKey(name: 'storage_mode') String? get storageMode;@JsonKey(name: 'min_days') int? get minDays;@JsonKey(name: 'max_days') int? get maxDays;@JsonKey(name: 'default_days') int get defaultDays;
/// Create a copy of ShelfLifeRuleDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ShelfLifeRuleDtoCopyWith<ShelfLifeRuleDto> get copyWith => _$ShelfLifeRuleDtoCopyWithImpl<ShelfLifeRuleDto>(this as ShelfLifeRuleDto, _$identity);

  /// Serializes this ShelfLifeRuleDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ShelfLifeRuleDto&&(identical(other.scope, scope) || other.scope == scope)&&(identical(other.storageMode, storageMode) || other.storageMode == storageMode)&&(identical(other.minDays, minDays) || other.minDays == minDays)&&(identical(other.maxDays, maxDays) || other.maxDays == maxDays)&&(identical(other.defaultDays, defaultDays) || other.defaultDays == defaultDays));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,scope,storageMode,minDays,maxDays,defaultDays);

@override
String toString() {
  return 'ShelfLifeRuleDto(scope: $scope, storageMode: $storageMode, minDays: $minDays, maxDays: $maxDays, defaultDays: $defaultDays)';
}


}

/// @nodoc
abstract mixin class $ShelfLifeRuleDtoCopyWith<$Res>  {
  factory $ShelfLifeRuleDtoCopyWith(ShelfLifeRuleDto value, $Res Function(ShelfLifeRuleDto) _then) = _$ShelfLifeRuleDtoCopyWithImpl;
@useResult
$Res call({
 String? scope,@JsonKey(name: 'storage_mode') String? storageMode,@JsonKey(name: 'min_days') int? minDays,@JsonKey(name: 'max_days') int? maxDays,@JsonKey(name: 'default_days') int defaultDays
});




}
/// @nodoc
class _$ShelfLifeRuleDtoCopyWithImpl<$Res>
    implements $ShelfLifeRuleDtoCopyWith<$Res> {
  _$ShelfLifeRuleDtoCopyWithImpl(this._self, this._then);

  final ShelfLifeRuleDto _self;
  final $Res Function(ShelfLifeRuleDto) _then;

/// Create a copy of ShelfLifeRuleDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? scope = freezed,Object? storageMode = freezed,Object? minDays = freezed,Object? maxDays = freezed,Object? defaultDays = null,}) {
  return _then(_self.copyWith(
scope: freezed == scope ? _self.scope : scope // ignore: cast_nullable_to_non_nullable
as String?,storageMode: freezed == storageMode ? _self.storageMode : storageMode // ignore: cast_nullable_to_non_nullable
as String?,minDays: freezed == minDays ? _self.minDays : minDays // ignore: cast_nullable_to_non_nullable
as int?,maxDays: freezed == maxDays ? _self.maxDays : maxDays // ignore: cast_nullable_to_non_nullable
as int?,defaultDays: null == defaultDays ? _self.defaultDays : defaultDays // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [ShelfLifeRuleDto].
extension ShelfLifeRuleDtoPatterns on ShelfLifeRuleDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ShelfLifeRuleDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ShelfLifeRuleDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ShelfLifeRuleDto value)  $default,){
final _that = this;
switch (_that) {
case _ShelfLifeRuleDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ShelfLifeRuleDto value)?  $default,){
final _that = this;
switch (_that) {
case _ShelfLifeRuleDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? scope, @JsonKey(name: 'storage_mode')  String? storageMode, @JsonKey(name: 'min_days')  int? minDays, @JsonKey(name: 'max_days')  int? maxDays, @JsonKey(name: 'default_days')  int defaultDays)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ShelfLifeRuleDto() when $default != null:
return $default(_that.scope,_that.storageMode,_that.minDays,_that.maxDays,_that.defaultDays);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? scope, @JsonKey(name: 'storage_mode')  String? storageMode, @JsonKey(name: 'min_days')  int? minDays, @JsonKey(name: 'max_days')  int? maxDays, @JsonKey(name: 'default_days')  int defaultDays)  $default,) {final _that = this;
switch (_that) {
case _ShelfLifeRuleDto():
return $default(_that.scope,_that.storageMode,_that.minDays,_that.maxDays,_that.defaultDays);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? scope, @JsonKey(name: 'storage_mode')  String? storageMode, @JsonKey(name: 'min_days')  int? minDays, @JsonKey(name: 'max_days')  int? maxDays, @JsonKey(name: 'default_days')  int defaultDays)?  $default,) {final _that = this;
switch (_that) {
case _ShelfLifeRuleDto() when $default != null:
return $default(_that.scope,_that.storageMode,_that.minDays,_that.maxDays,_that.defaultDays);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ShelfLifeRuleDto implements ShelfLifeRuleDto {
  const _ShelfLifeRuleDto({this.scope, @JsonKey(name: 'storage_mode') this.storageMode, @JsonKey(name: 'min_days') this.minDays, @JsonKey(name: 'max_days') this.maxDays, @JsonKey(name: 'default_days') this.defaultDays = 0});
  factory _ShelfLifeRuleDto.fromJson(Map<String, dynamic> json) => _$ShelfLifeRuleDtoFromJson(json);

@override final  String? scope;
@override@JsonKey(name: 'storage_mode') final  String? storageMode;
@override@JsonKey(name: 'min_days') final  int? minDays;
@override@JsonKey(name: 'max_days') final  int? maxDays;
@override@JsonKey(name: 'default_days') final  int defaultDays;

/// Create a copy of ShelfLifeRuleDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ShelfLifeRuleDtoCopyWith<_ShelfLifeRuleDto> get copyWith => __$ShelfLifeRuleDtoCopyWithImpl<_ShelfLifeRuleDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ShelfLifeRuleDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ShelfLifeRuleDto&&(identical(other.scope, scope) || other.scope == scope)&&(identical(other.storageMode, storageMode) || other.storageMode == storageMode)&&(identical(other.minDays, minDays) || other.minDays == minDays)&&(identical(other.maxDays, maxDays) || other.maxDays == maxDays)&&(identical(other.defaultDays, defaultDays) || other.defaultDays == defaultDays));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,scope,storageMode,minDays,maxDays,defaultDays);

@override
String toString() {
  return 'ShelfLifeRuleDto(scope: $scope, storageMode: $storageMode, minDays: $minDays, maxDays: $maxDays, defaultDays: $defaultDays)';
}


}

/// @nodoc
abstract mixin class _$ShelfLifeRuleDtoCopyWith<$Res> implements $ShelfLifeRuleDtoCopyWith<$Res> {
  factory _$ShelfLifeRuleDtoCopyWith(_ShelfLifeRuleDto value, $Res Function(_ShelfLifeRuleDto) _then) = __$ShelfLifeRuleDtoCopyWithImpl;
@override @useResult
$Res call({
 String? scope,@JsonKey(name: 'storage_mode') String? storageMode,@JsonKey(name: 'min_days') int? minDays,@JsonKey(name: 'max_days') int? maxDays,@JsonKey(name: 'default_days') int defaultDays
});




}
/// @nodoc
class __$ShelfLifeRuleDtoCopyWithImpl<$Res>
    implements _$ShelfLifeRuleDtoCopyWith<$Res> {
  __$ShelfLifeRuleDtoCopyWithImpl(this._self, this._then);

  final _ShelfLifeRuleDto _self;
  final $Res Function(_ShelfLifeRuleDto) _then;

/// Create a copy of ShelfLifeRuleDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? scope = freezed,Object? storageMode = freezed,Object? minDays = freezed,Object? maxDays = freezed,Object? defaultDays = null,}) {
  return _then(_ShelfLifeRuleDto(
scope: freezed == scope ? _self.scope : scope // ignore: cast_nullable_to_non_nullable
as String?,storageMode: freezed == storageMode ? _self.storageMode : storageMode // ignore: cast_nullable_to_non_nullable
as String?,minDays: freezed == minDays ? _self.minDays : minDays // ignore: cast_nullable_to_non_nullable
as int?,maxDays: freezed == maxDays ? _self.maxDays : maxDays // ignore: cast_nullable_to_non_nullable
as int?,defaultDays: null == defaultDays ? _self.defaultDays : defaultDays // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on
