// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'shopping_list_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ShoppingListItemDto {

 String get id;@JsonKey(name: 'master_ingredient_id') String? get masterIngredientId;@JsonKey(name: 'custom_name') String? get customName; String get name;@JsonKey(name: 'required_quantity') double get requiredQuantity;@JsonKey(name: 'available_quantity') double get availableQuantity;@JsonKey(name: 'missing_quantity') double get missingQuantity; String get unit;@JsonKey(name: 'estimated_cost') num? get estimatedCost;@JsonKey(name: 'is_checked') bool get isChecked;@JsonKey(name: 'is_generated') bool get isGenerated;@JsonKey(name: 'source_recipe_ids') List<String> get sourceRecipeIds;@JsonKey(name: 'inventory_batch_id') String? get inventoryBatchId;
/// Create a copy of ShoppingListItemDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ShoppingListItemDtoCopyWith<ShoppingListItemDto> get copyWith => _$ShoppingListItemDtoCopyWithImpl<ShoppingListItemDto>(this as ShoppingListItemDto, _$identity);

  /// Serializes this ShoppingListItemDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ShoppingListItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId)&&(identical(other.customName, customName) || other.customName == customName)&&(identical(other.name, name) || other.name == name)&&(identical(other.requiredQuantity, requiredQuantity) || other.requiredQuantity == requiredQuantity)&&(identical(other.availableQuantity, availableQuantity) || other.availableQuantity == availableQuantity)&&(identical(other.missingQuantity, missingQuantity) || other.missingQuantity == missingQuantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.estimatedCost, estimatedCost) || other.estimatedCost == estimatedCost)&&(identical(other.isChecked, isChecked) || other.isChecked == isChecked)&&(identical(other.isGenerated, isGenerated) || other.isGenerated == isGenerated)&&const DeepCollectionEquality().equals(other.sourceRecipeIds, sourceRecipeIds)&&(identical(other.inventoryBatchId, inventoryBatchId) || other.inventoryBatchId == inventoryBatchId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,masterIngredientId,customName,name,requiredQuantity,availableQuantity,missingQuantity,unit,estimatedCost,isChecked,isGenerated,const DeepCollectionEquality().hash(sourceRecipeIds),inventoryBatchId);

@override
String toString() {
  return 'ShoppingListItemDto(id: $id, masterIngredientId: $masterIngredientId, customName: $customName, name: $name, requiredQuantity: $requiredQuantity, availableQuantity: $availableQuantity, missingQuantity: $missingQuantity, unit: $unit, estimatedCost: $estimatedCost, isChecked: $isChecked, isGenerated: $isGenerated, sourceRecipeIds: $sourceRecipeIds, inventoryBatchId: $inventoryBatchId)';
}


}

/// @nodoc
abstract mixin class $ShoppingListItemDtoCopyWith<$Res>  {
  factory $ShoppingListItemDtoCopyWith(ShoppingListItemDto value, $Res Function(ShoppingListItemDto) _then) = _$ShoppingListItemDtoCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'master_ingredient_id') String? masterIngredientId,@JsonKey(name: 'custom_name') String? customName, String name,@JsonKey(name: 'required_quantity') double requiredQuantity,@JsonKey(name: 'available_quantity') double availableQuantity,@JsonKey(name: 'missing_quantity') double missingQuantity, String unit,@JsonKey(name: 'estimated_cost') num? estimatedCost,@JsonKey(name: 'is_checked') bool isChecked,@JsonKey(name: 'is_generated') bool isGenerated,@JsonKey(name: 'source_recipe_ids') List<String> sourceRecipeIds,@JsonKey(name: 'inventory_batch_id') String? inventoryBatchId
});




}
/// @nodoc
class _$ShoppingListItemDtoCopyWithImpl<$Res>
    implements $ShoppingListItemDtoCopyWith<$Res> {
  _$ShoppingListItemDtoCopyWithImpl(this._self, this._then);

  final ShoppingListItemDto _self;
  final $Res Function(ShoppingListItemDto) _then;

/// Create a copy of ShoppingListItemDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? masterIngredientId = freezed,Object? customName = freezed,Object? name = null,Object? requiredQuantity = null,Object? availableQuantity = null,Object? missingQuantity = null,Object? unit = null,Object? estimatedCost = freezed,Object? isChecked = null,Object? isGenerated = null,Object? sourceRecipeIds = null,Object? inventoryBatchId = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,customName: freezed == customName ? _self.customName : customName // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,requiredQuantity: null == requiredQuantity ? _self.requiredQuantity : requiredQuantity // ignore: cast_nullable_to_non_nullable
as double,availableQuantity: null == availableQuantity ? _self.availableQuantity : availableQuantity // ignore: cast_nullable_to_non_nullable
as double,missingQuantity: null == missingQuantity ? _self.missingQuantity : missingQuantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,estimatedCost: freezed == estimatedCost ? _self.estimatedCost : estimatedCost // ignore: cast_nullable_to_non_nullable
as num?,isChecked: null == isChecked ? _self.isChecked : isChecked // ignore: cast_nullable_to_non_nullable
as bool,isGenerated: null == isGenerated ? _self.isGenerated : isGenerated // ignore: cast_nullable_to_non_nullable
as bool,sourceRecipeIds: null == sourceRecipeIds ? _self.sourceRecipeIds : sourceRecipeIds // ignore: cast_nullable_to_non_nullable
as List<String>,inventoryBatchId: freezed == inventoryBatchId ? _self.inventoryBatchId : inventoryBatchId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ShoppingListItemDto].
extension ShoppingListItemDtoPatterns on ShoppingListItemDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ShoppingListItemDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ShoppingListItemDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ShoppingListItemDto value)  $default,){
final _that = this;
switch (_that) {
case _ShoppingListItemDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ShoppingListItemDto value)?  $default,){
final _that = this;
switch (_that) {
case _ShoppingListItemDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId, @JsonKey(name: 'custom_name')  String? customName,  String name, @JsonKey(name: 'required_quantity')  double requiredQuantity, @JsonKey(name: 'available_quantity')  double availableQuantity, @JsonKey(name: 'missing_quantity')  double missingQuantity,  String unit, @JsonKey(name: 'estimated_cost')  num? estimatedCost, @JsonKey(name: 'is_checked')  bool isChecked, @JsonKey(name: 'is_generated')  bool isGenerated, @JsonKey(name: 'source_recipe_ids')  List<String> sourceRecipeIds, @JsonKey(name: 'inventory_batch_id')  String? inventoryBatchId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ShoppingListItemDto() when $default != null:
return $default(_that.id,_that.masterIngredientId,_that.customName,_that.name,_that.requiredQuantity,_that.availableQuantity,_that.missingQuantity,_that.unit,_that.estimatedCost,_that.isChecked,_that.isGenerated,_that.sourceRecipeIds,_that.inventoryBatchId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId, @JsonKey(name: 'custom_name')  String? customName,  String name, @JsonKey(name: 'required_quantity')  double requiredQuantity, @JsonKey(name: 'available_quantity')  double availableQuantity, @JsonKey(name: 'missing_quantity')  double missingQuantity,  String unit, @JsonKey(name: 'estimated_cost')  num? estimatedCost, @JsonKey(name: 'is_checked')  bool isChecked, @JsonKey(name: 'is_generated')  bool isGenerated, @JsonKey(name: 'source_recipe_ids')  List<String> sourceRecipeIds, @JsonKey(name: 'inventory_batch_id')  String? inventoryBatchId)  $default,) {final _that = this;
switch (_that) {
case _ShoppingListItemDto():
return $default(_that.id,_that.masterIngredientId,_that.customName,_that.name,_that.requiredQuantity,_that.availableQuantity,_that.missingQuantity,_that.unit,_that.estimatedCost,_that.isChecked,_that.isGenerated,_that.sourceRecipeIds,_that.inventoryBatchId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId, @JsonKey(name: 'custom_name')  String? customName,  String name, @JsonKey(name: 'required_quantity')  double requiredQuantity, @JsonKey(name: 'available_quantity')  double availableQuantity, @JsonKey(name: 'missing_quantity')  double missingQuantity,  String unit, @JsonKey(name: 'estimated_cost')  num? estimatedCost, @JsonKey(name: 'is_checked')  bool isChecked, @JsonKey(name: 'is_generated')  bool isGenerated, @JsonKey(name: 'source_recipe_ids')  List<String> sourceRecipeIds, @JsonKey(name: 'inventory_batch_id')  String? inventoryBatchId)?  $default,) {final _that = this;
switch (_that) {
case _ShoppingListItemDto() when $default != null:
return $default(_that.id,_that.masterIngredientId,_that.customName,_that.name,_that.requiredQuantity,_that.availableQuantity,_that.missingQuantity,_that.unit,_that.estimatedCost,_that.isChecked,_that.isGenerated,_that.sourceRecipeIds,_that.inventoryBatchId);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ShoppingListItemDto extends ShoppingListItemDto {
  const _ShoppingListItemDto({required this.id, @JsonKey(name: 'master_ingredient_id') this.masterIngredientId, @JsonKey(name: 'custom_name') this.customName, required this.name, @JsonKey(name: 'required_quantity') this.requiredQuantity = 0, @JsonKey(name: 'available_quantity') this.availableQuantity = 0, @JsonKey(name: 'missing_quantity') this.missingQuantity = 0, required this.unit, @JsonKey(name: 'estimated_cost') this.estimatedCost, @JsonKey(name: 'is_checked') this.isChecked = false, @JsonKey(name: 'is_generated') this.isGenerated = true, @JsonKey(name: 'source_recipe_ids') final  List<String> sourceRecipeIds = const <String>[], @JsonKey(name: 'inventory_batch_id') this.inventoryBatchId}): _sourceRecipeIds = sourceRecipeIds,super._();
  factory _ShoppingListItemDto.fromJson(Map<String, dynamic> json) => _$ShoppingListItemDtoFromJson(json);

@override final  String id;
@override@JsonKey(name: 'master_ingredient_id') final  String? masterIngredientId;
@override@JsonKey(name: 'custom_name') final  String? customName;
@override final  String name;
@override@JsonKey(name: 'required_quantity') final  double requiredQuantity;
@override@JsonKey(name: 'available_quantity') final  double availableQuantity;
@override@JsonKey(name: 'missing_quantity') final  double missingQuantity;
@override final  String unit;
@override@JsonKey(name: 'estimated_cost') final  num? estimatedCost;
@override@JsonKey(name: 'is_checked') final  bool isChecked;
@override@JsonKey(name: 'is_generated') final  bool isGenerated;
 final  List<String> _sourceRecipeIds;
@override@JsonKey(name: 'source_recipe_ids') List<String> get sourceRecipeIds {
  if (_sourceRecipeIds is EqualUnmodifiableListView) return _sourceRecipeIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_sourceRecipeIds);
}

@override@JsonKey(name: 'inventory_batch_id') final  String? inventoryBatchId;

/// Create a copy of ShoppingListItemDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ShoppingListItemDtoCopyWith<_ShoppingListItemDto> get copyWith => __$ShoppingListItemDtoCopyWithImpl<_ShoppingListItemDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ShoppingListItemDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ShoppingListItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId)&&(identical(other.customName, customName) || other.customName == customName)&&(identical(other.name, name) || other.name == name)&&(identical(other.requiredQuantity, requiredQuantity) || other.requiredQuantity == requiredQuantity)&&(identical(other.availableQuantity, availableQuantity) || other.availableQuantity == availableQuantity)&&(identical(other.missingQuantity, missingQuantity) || other.missingQuantity == missingQuantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.estimatedCost, estimatedCost) || other.estimatedCost == estimatedCost)&&(identical(other.isChecked, isChecked) || other.isChecked == isChecked)&&(identical(other.isGenerated, isGenerated) || other.isGenerated == isGenerated)&&const DeepCollectionEquality().equals(other._sourceRecipeIds, _sourceRecipeIds)&&(identical(other.inventoryBatchId, inventoryBatchId) || other.inventoryBatchId == inventoryBatchId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,masterIngredientId,customName,name,requiredQuantity,availableQuantity,missingQuantity,unit,estimatedCost,isChecked,isGenerated,const DeepCollectionEquality().hash(_sourceRecipeIds),inventoryBatchId);

@override
String toString() {
  return 'ShoppingListItemDto(id: $id, masterIngredientId: $masterIngredientId, customName: $customName, name: $name, requiredQuantity: $requiredQuantity, availableQuantity: $availableQuantity, missingQuantity: $missingQuantity, unit: $unit, estimatedCost: $estimatedCost, isChecked: $isChecked, isGenerated: $isGenerated, sourceRecipeIds: $sourceRecipeIds, inventoryBatchId: $inventoryBatchId)';
}


}

/// @nodoc
abstract mixin class _$ShoppingListItemDtoCopyWith<$Res> implements $ShoppingListItemDtoCopyWith<$Res> {
  factory _$ShoppingListItemDtoCopyWith(_ShoppingListItemDto value, $Res Function(_ShoppingListItemDto) _then) = __$ShoppingListItemDtoCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'master_ingredient_id') String? masterIngredientId,@JsonKey(name: 'custom_name') String? customName, String name,@JsonKey(name: 'required_quantity') double requiredQuantity,@JsonKey(name: 'available_quantity') double availableQuantity,@JsonKey(name: 'missing_quantity') double missingQuantity, String unit,@JsonKey(name: 'estimated_cost') num? estimatedCost,@JsonKey(name: 'is_checked') bool isChecked,@JsonKey(name: 'is_generated') bool isGenerated,@JsonKey(name: 'source_recipe_ids') List<String> sourceRecipeIds,@JsonKey(name: 'inventory_batch_id') String? inventoryBatchId
});




}
/// @nodoc
class __$ShoppingListItemDtoCopyWithImpl<$Res>
    implements _$ShoppingListItemDtoCopyWith<$Res> {
  __$ShoppingListItemDtoCopyWithImpl(this._self, this._then);

  final _ShoppingListItemDto _self;
  final $Res Function(_ShoppingListItemDto) _then;

/// Create a copy of ShoppingListItemDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? masterIngredientId = freezed,Object? customName = freezed,Object? name = null,Object? requiredQuantity = null,Object? availableQuantity = null,Object? missingQuantity = null,Object? unit = null,Object? estimatedCost = freezed,Object? isChecked = null,Object? isGenerated = null,Object? sourceRecipeIds = null,Object? inventoryBatchId = freezed,}) {
  return _then(_ShoppingListItemDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,customName: freezed == customName ? _self.customName : customName // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,requiredQuantity: null == requiredQuantity ? _self.requiredQuantity : requiredQuantity // ignore: cast_nullable_to_non_nullable
as double,availableQuantity: null == availableQuantity ? _self.availableQuantity : availableQuantity // ignore: cast_nullable_to_non_nullable
as double,missingQuantity: null == missingQuantity ? _self.missingQuantity : missingQuantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,estimatedCost: freezed == estimatedCost ? _self.estimatedCost : estimatedCost // ignore: cast_nullable_to_non_nullable
as num?,isChecked: null == isChecked ? _self.isChecked : isChecked // ignore: cast_nullable_to_non_nullable
as bool,isGenerated: null == isGenerated ? _self.isGenerated : isGenerated // ignore: cast_nullable_to_non_nullable
as bool,sourceRecipeIds: null == sourceRecipeIds ? _self._sourceRecipeIds : sourceRecipeIds // ignore: cast_nullable_to_non_nullable
as List<String>,inventoryBatchId: freezed == inventoryBatchId ? _self.inventoryBatchId : inventoryBatchId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ShoppingListDto {

 String get id;@JsonKey(name: 'meal_plan_id') String? get mealPlanId; String get status;@JsonKey(name: 'generated_at') DateTime? get generatedAt; List<ShoppingListItemDto> get items;
/// Create a copy of ShoppingListDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ShoppingListDtoCopyWith<ShoppingListDto> get copyWith => _$ShoppingListDtoCopyWithImpl<ShoppingListDto>(this as ShoppingListDto, _$identity);

  /// Serializes this ShoppingListDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ShoppingListDto&&(identical(other.id, id) || other.id == id)&&(identical(other.mealPlanId, mealPlanId) || other.mealPlanId == mealPlanId)&&(identical(other.status, status) || other.status == status)&&(identical(other.generatedAt, generatedAt) || other.generatedAt == generatedAt)&&const DeepCollectionEquality().equals(other.items, items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,mealPlanId,status,generatedAt,const DeepCollectionEquality().hash(items));

@override
String toString() {
  return 'ShoppingListDto(id: $id, mealPlanId: $mealPlanId, status: $status, generatedAt: $generatedAt, items: $items)';
}


}

/// @nodoc
abstract mixin class $ShoppingListDtoCopyWith<$Res>  {
  factory $ShoppingListDtoCopyWith(ShoppingListDto value, $Res Function(ShoppingListDto) _then) = _$ShoppingListDtoCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'meal_plan_id') String? mealPlanId, String status,@JsonKey(name: 'generated_at') DateTime? generatedAt, List<ShoppingListItemDto> items
});




}
/// @nodoc
class _$ShoppingListDtoCopyWithImpl<$Res>
    implements $ShoppingListDtoCopyWith<$Res> {
  _$ShoppingListDtoCopyWithImpl(this._self, this._then);

  final ShoppingListDto _self;
  final $Res Function(ShoppingListDto) _then;

/// Create a copy of ShoppingListDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? mealPlanId = freezed,Object? status = null,Object? generatedAt = freezed,Object? items = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,mealPlanId: freezed == mealPlanId ? _self.mealPlanId : mealPlanId // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,generatedAt: freezed == generatedAt ? _self.generatedAt : generatedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<ShoppingListItemDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [ShoppingListDto].
extension ShoppingListDtoPatterns on ShoppingListDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ShoppingListDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ShoppingListDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ShoppingListDto value)  $default,){
final _that = this;
switch (_that) {
case _ShoppingListDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ShoppingListDto value)?  $default,){
final _that = this;
switch (_that) {
case _ShoppingListDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'meal_plan_id')  String? mealPlanId,  String status, @JsonKey(name: 'generated_at')  DateTime? generatedAt,  List<ShoppingListItemDto> items)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ShoppingListDto() when $default != null:
return $default(_that.id,_that.mealPlanId,_that.status,_that.generatedAt,_that.items);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'meal_plan_id')  String? mealPlanId,  String status, @JsonKey(name: 'generated_at')  DateTime? generatedAt,  List<ShoppingListItemDto> items)  $default,) {final _that = this;
switch (_that) {
case _ShoppingListDto():
return $default(_that.id,_that.mealPlanId,_that.status,_that.generatedAt,_that.items);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'meal_plan_id')  String? mealPlanId,  String status, @JsonKey(name: 'generated_at')  DateTime? generatedAt,  List<ShoppingListItemDto> items)?  $default,) {final _that = this;
switch (_that) {
case _ShoppingListDto() when $default != null:
return $default(_that.id,_that.mealPlanId,_that.status,_that.generatedAt,_that.items);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ShoppingListDto extends ShoppingListDto {
  const _ShoppingListDto({required this.id, @JsonKey(name: 'meal_plan_id') this.mealPlanId, this.status = 'ACTIVE', @JsonKey(name: 'generated_at') this.generatedAt, final  List<ShoppingListItemDto> items = const <ShoppingListItemDto>[]}): _items = items,super._();
  factory _ShoppingListDto.fromJson(Map<String, dynamic> json) => _$ShoppingListDtoFromJson(json);

@override final  String id;
@override@JsonKey(name: 'meal_plan_id') final  String? mealPlanId;
@override@JsonKey() final  String status;
@override@JsonKey(name: 'generated_at') final  DateTime? generatedAt;
 final  List<ShoppingListItemDto> _items;
@override@JsonKey() List<ShoppingListItemDto> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


/// Create a copy of ShoppingListDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ShoppingListDtoCopyWith<_ShoppingListDto> get copyWith => __$ShoppingListDtoCopyWithImpl<_ShoppingListDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ShoppingListDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ShoppingListDto&&(identical(other.id, id) || other.id == id)&&(identical(other.mealPlanId, mealPlanId) || other.mealPlanId == mealPlanId)&&(identical(other.status, status) || other.status == status)&&(identical(other.generatedAt, generatedAt) || other.generatedAt == generatedAt)&&const DeepCollectionEquality().equals(other._items, _items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,mealPlanId,status,generatedAt,const DeepCollectionEquality().hash(_items));

@override
String toString() {
  return 'ShoppingListDto(id: $id, mealPlanId: $mealPlanId, status: $status, generatedAt: $generatedAt, items: $items)';
}


}

/// @nodoc
abstract mixin class _$ShoppingListDtoCopyWith<$Res> implements $ShoppingListDtoCopyWith<$Res> {
  factory _$ShoppingListDtoCopyWith(_ShoppingListDto value, $Res Function(_ShoppingListDto) _then) = __$ShoppingListDtoCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'meal_plan_id') String? mealPlanId, String status,@JsonKey(name: 'generated_at') DateTime? generatedAt, List<ShoppingListItemDto> items
});




}
/// @nodoc
class __$ShoppingListDtoCopyWithImpl<$Res>
    implements _$ShoppingListDtoCopyWith<$Res> {
  __$ShoppingListDtoCopyWithImpl(this._self, this._then);

  final _ShoppingListDto _self;
  final $Res Function(_ShoppingListDto) _then;

/// Create a copy of ShoppingListDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? mealPlanId = freezed,Object? status = null,Object? generatedAt = freezed,Object? items = null,}) {
  return _then(_ShoppingListDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,mealPlanId: freezed == mealPlanId ? _self.mealPlanId : mealPlanId // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,generatedAt: freezed == generatedAt ? _self.generatedAt : generatedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<ShoppingListItemDto>,
  ));
}


}

// dart format on
