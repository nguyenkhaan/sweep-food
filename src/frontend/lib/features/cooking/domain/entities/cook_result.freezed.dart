// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'cook_result.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$PantryChange {

 String get name; MeasurementUnit get unit; double get before; double get after; bool get nearExpiryUsed; String? get pantryItemId;
/// Create a copy of PantryChange
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PantryChangeCopyWith<PantryChange> get copyWith => _$PantryChangeCopyWithImpl<PantryChange>(this as PantryChange, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PantryChange&&(identical(other.name, name) || other.name == name)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.before, before) || other.before == before)&&(identical(other.after, after) || other.after == after)&&(identical(other.nearExpiryUsed, nearExpiryUsed) || other.nearExpiryUsed == nearExpiryUsed)&&(identical(other.pantryItemId, pantryItemId) || other.pantryItemId == pantryItemId));
}


@override
int get hashCode => Object.hash(runtimeType,name,unit,before,after,nearExpiryUsed,pantryItemId);

@override
String toString() {
  return 'PantryChange(name: $name, unit: $unit, before: $before, after: $after, nearExpiryUsed: $nearExpiryUsed, pantryItemId: $pantryItemId)';
}


}

/// @nodoc
abstract mixin class $PantryChangeCopyWith<$Res>  {
  factory $PantryChangeCopyWith(PantryChange value, $Res Function(PantryChange) _then) = _$PantryChangeCopyWithImpl;
@useResult
$Res call({
 String name, MeasurementUnit unit, double before, double after, bool nearExpiryUsed, String? pantryItemId
});




}
/// @nodoc
class _$PantryChangeCopyWithImpl<$Res>
    implements $PantryChangeCopyWith<$Res> {
  _$PantryChangeCopyWithImpl(this._self, this._then);

  final PantryChange _self;
  final $Res Function(PantryChange) _then;

/// Create a copy of PantryChange
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? unit = null,Object? before = null,Object? after = null,Object? nearExpiryUsed = null,Object? pantryItemId = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,before: null == before ? _self.before : before // ignore: cast_nullable_to_non_nullable
as double,after: null == after ? _self.after : after // ignore: cast_nullable_to_non_nullable
as double,nearExpiryUsed: null == nearExpiryUsed ? _self.nearExpiryUsed : nearExpiryUsed // ignore: cast_nullable_to_non_nullable
as bool,pantryItemId: freezed == pantryItemId ? _self.pantryItemId : pantryItemId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [PantryChange].
extension PantryChangePatterns on PantryChange {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PantryChange value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PantryChange() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PantryChange value)  $default,){
final _that = this;
switch (_that) {
case _PantryChange():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PantryChange value)?  $default,){
final _that = this;
switch (_that) {
case _PantryChange() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String name,  MeasurementUnit unit,  double before,  double after,  bool nearExpiryUsed,  String? pantryItemId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PantryChange() when $default != null:
return $default(_that.name,_that.unit,_that.before,_that.after,_that.nearExpiryUsed,_that.pantryItemId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String name,  MeasurementUnit unit,  double before,  double after,  bool nearExpiryUsed,  String? pantryItemId)  $default,) {final _that = this;
switch (_that) {
case _PantryChange():
return $default(_that.name,_that.unit,_that.before,_that.after,_that.nearExpiryUsed,_that.pantryItemId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String name,  MeasurementUnit unit,  double before,  double after,  bool nearExpiryUsed,  String? pantryItemId)?  $default,) {final _that = this;
switch (_that) {
case _PantryChange() when $default != null:
return $default(_that.name,_that.unit,_that.before,_that.after,_that.nearExpiryUsed,_that.pantryItemId);case _:
  return null;

}
}

}

/// @nodoc


class _PantryChange extends PantryChange {
  const _PantryChange({required this.name, required this.unit, required this.before, required this.after, this.nearExpiryUsed = false, this.pantryItemId}): super._();
  

@override final  String name;
@override final  MeasurementUnit unit;
@override final  double before;
@override final  double after;
@override@JsonKey() final  bool nearExpiryUsed;
@override final  String? pantryItemId;

/// Create a copy of PantryChange
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PantryChangeCopyWith<_PantryChange> get copyWith => __$PantryChangeCopyWithImpl<_PantryChange>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _PantryChange&&(identical(other.name, name) || other.name == name)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.before, before) || other.before == before)&&(identical(other.after, after) || other.after == after)&&(identical(other.nearExpiryUsed, nearExpiryUsed) || other.nearExpiryUsed == nearExpiryUsed)&&(identical(other.pantryItemId, pantryItemId) || other.pantryItemId == pantryItemId));
}


@override
int get hashCode => Object.hash(runtimeType,name,unit,before,after,nearExpiryUsed,pantryItemId);

@override
String toString() {
  return 'PantryChange(name: $name, unit: $unit, before: $before, after: $after, nearExpiryUsed: $nearExpiryUsed, pantryItemId: $pantryItemId)';
}


}

/// @nodoc
abstract mixin class _$PantryChangeCopyWith<$Res> implements $PantryChangeCopyWith<$Res> {
  factory _$PantryChangeCopyWith(_PantryChange value, $Res Function(_PantryChange) _then) = __$PantryChangeCopyWithImpl;
@override @useResult
$Res call({
 String name, MeasurementUnit unit, double before, double after, bool nearExpiryUsed, String? pantryItemId
});




}
/// @nodoc
class __$PantryChangeCopyWithImpl<$Res>
    implements _$PantryChangeCopyWith<$Res> {
  __$PantryChangeCopyWithImpl(this._self, this._then);

  final _PantryChange _self;
  final $Res Function(_PantryChange) _then;

/// Create a copy of PantryChange
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? unit = null,Object? before = null,Object? after = null,Object? nearExpiryUsed = null,Object? pantryItemId = freezed,}) {
  return _then(_PantryChange(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,before: null == before ? _self.before : before // ignore: cast_nullable_to_non_nullable
as double,after: null == after ? _self.after : after // ignore: cast_nullable_to_non_nullable
as double,nearExpiryUsed: null == nearExpiryUsed ? _self.nearExpiryUsed : nearExpiryUsed // ignore: cast_nullable_to_non_nullable
as bool,pantryItemId: freezed == pantryItemId ? _self.pantryItemId : pantryItemId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

/// @nodoc
mixin _$CookResult {

 String get dishId; String get dishName; String get sessionId; List<PantryChange> get changes;/// Post-cook state of the touched pantry items, for the list to splice in.
 List<PantryItem> get updatedPantryItems;/// Ids of pantry items that dropped to zero and were marked used.
 List<String> get depletedItemIds; int get nearExpiryUsedCount; double get wasteAvoidedGrams;
/// Create a copy of CookResult
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookResultCopyWith<CookResult> get copyWith => _$CookResultCopyWithImpl<CookResult>(this as CookResult, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookResult&&(identical(other.dishId, dishId) || other.dishId == dishId)&&(identical(other.dishName, dishName) || other.dishName == dishName)&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId)&&const DeepCollectionEquality().equals(other.changes, changes)&&const DeepCollectionEquality().equals(other.updatedPantryItems, updatedPantryItems)&&const DeepCollectionEquality().equals(other.depletedItemIds, depletedItemIds)&&(identical(other.nearExpiryUsedCount, nearExpiryUsedCount) || other.nearExpiryUsedCount == nearExpiryUsedCount)&&(identical(other.wasteAvoidedGrams, wasteAvoidedGrams) || other.wasteAvoidedGrams == wasteAvoidedGrams));
}


@override
int get hashCode => Object.hash(runtimeType,dishId,dishName,sessionId,const DeepCollectionEquality().hash(changes),const DeepCollectionEquality().hash(updatedPantryItems),const DeepCollectionEquality().hash(depletedItemIds),nearExpiryUsedCount,wasteAvoidedGrams);

@override
String toString() {
  return 'CookResult(dishId: $dishId, dishName: $dishName, sessionId: $sessionId, changes: $changes, updatedPantryItems: $updatedPantryItems, depletedItemIds: $depletedItemIds, nearExpiryUsedCount: $nearExpiryUsedCount, wasteAvoidedGrams: $wasteAvoidedGrams)';
}


}

/// @nodoc
abstract mixin class $CookResultCopyWith<$Res>  {
  factory $CookResultCopyWith(CookResult value, $Res Function(CookResult) _then) = _$CookResultCopyWithImpl;
@useResult
$Res call({
 String dishId, String dishName, String sessionId, List<PantryChange> changes, List<PantryItem> updatedPantryItems, List<String> depletedItemIds, int nearExpiryUsedCount, double wasteAvoidedGrams
});




}
/// @nodoc
class _$CookResultCopyWithImpl<$Res>
    implements $CookResultCopyWith<$Res> {
  _$CookResultCopyWithImpl(this._self, this._then);

  final CookResult _self;
  final $Res Function(CookResult) _then;

/// Create a copy of CookResult
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? dishId = null,Object? dishName = null,Object? sessionId = null,Object? changes = null,Object? updatedPantryItems = null,Object? depletedItemIds = null,Object? nearExpiryUsedCount = null,Object? wasteAvoidedGrams = null,}) {
  return _then(_self.copyWith(
dishId: null == dishId ? _self.dishId : dishId // ignore: cast_nullable_to_non_nullable
as String,dishName: null == dishName ? _self.dishName : dishName // ignore: cast_nullable_to_non_nullable
as String,sessionId: null == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String,changes: null == changes ? _self.changes : changes // ignore: cast_nullable_to_non_nullable
as List<PantryChange>,updatedPantryItems: null == updatedPantryItems ? _self.updatedPantryItems : updatedPantryItems // ignore: cast_nullable_to_non_nullable
as List<PantryItem>,depletedItemIds: null == depletedItemIds ? _self.depletedItemIds : depletedItemIds // ignore: cast_nullable_to_non_nullable
as List<String>,nearExpiryUsedCount: null == nearExpiryUsedCount ? _self.nearExpiryUsedCount : nearExpiryUsedCount // ignore: cast_nullable_to_non_nullable
as int,wasteAvoidedGrams: null == wasteAvoidedGrams ? _self.wasteAvoidedGrams : wasteAvoidedGrams // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

}


/// Adds pattern-matching-related methods to [CookResult].
extension CookResultPatterns on CookResult {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookResult value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookResult() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookResult value)  $default,){
final _that = this;
switch (_that) {
case _CookResult():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookResult value)?  $default,){
final _that = this;
switch (_that) {
case _CookResult() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String dishId,  String dishName,  String sessionId,  List<PantryChange> changes,  List<PantryItem> updatedPantryItems,  List<String> depletedItemIds,  int nearExpiryUsedCount,  double wasteAvoidedGrams)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookResult() when $default != null:
return $default(_that.dishId,_that.dishName,_that.sessionId,_that.changes,_that.updatedPantryItems,_that.depletedItemIds,_that.nearExpiryUsedCount,_that.wasteAvoidedGrams);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String dishId,  String dishName,  String sessionId,  List<PantryChange> changes,  List<PantryItem> updatedPantryItems,  List<String> depletedItemIds,  int nearExpiryUsedCount,  double wasteAvoidedGrams)  $default,) {final _that = this;
switch (_that) {
case _CookResult():
return $default(_that.dishId,_that.dishName,_that.sessionId,_that.changes,_that.updatedPantryItems,_that.depletedItemIds,_that.nearExpiryUsedCount,_that.wasteAvoidedGrams);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String dishId,  String dishName,  String sessionId,  List<PantryChange> changes,  List<PantryItem> updatedPantryItems,  List<String> depletedItemIds,  int nearExpiryUsedCount,  double wasteAvoidedGrams)?  $default,) {final _that = this;
switch (_that) {
case _CookResult() when $default != null:
return $default(_that.dishId,_that.dishName,_that.sessionId,_that.changes,_that.updatedPantryItems,_that.depletedItemIds,_that.nearExpiryUsedCount,_that.wasteAvoidedGrams);case _:
  return null;

}
}

}

/// @nodoc


class _CookResult extends CookResult {
  const _CookResult({this.dishId = '', this.dishName = '', this.sessionId = '', final  List<PantryChange> changes = const <PantryChange>[], final  List<PantryItem> updatedPantryItems = const <PantryItem>[], final  List<String> depletedItemIds = const <String>[], this.nearExpiryUsedCount = 0, this.wasteAvoidedGrams = 0}): _changes = changes,_updatedPantryItems = updatedPantryItems,_depletedItemIds = depletedItemIds,super._();
  

@override@JsonKey() final  String dishId;
@override@JsonKey() final  String dishName;
@override@JsonKey() final  String sessionId;
 final  List<PantryChange> _changes;
@override@JsonKey() List<PantryChange> get changes {
  if (_changes is EqualUnmodifiableListView) return _changes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_changes);
}

/// Post-cook state of the touched pantry items, for the list to splice in.
 final  List<PantryItem> _updatedPantryItems;
/// Post-cook state of the touched pantry items, for the list to splice in.
@override@JsonKey() List<PantryItem> get updatedPantryItems {
  if (_updatedPantryItems is EqualUnmodifiableListView) return _updatedPantryItems;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_updatedPantryItems);
}

/// Ids of pantry items that dropped to zero and were marked used.
 final  List<String> _depletedItemIds;
/// Ids of pantry items that dropped to zero and were marked used.
@override@JsonKey() List<String> get depletedItemIds {
  if (_depletedItemIds is EqualUnmodifiableListView) return _depletedItemIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_depletedItemIds);
}

@override@JsonKey() final  int nearExpiryUsedCount;
@override@JsonKey() final  double wasteAvoidedGrams;

/// Create a copy of CookResult
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookResultCopyWith<_CookResult> get copyWith => __$CookResultCopyWithImpl<_CookResult>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookResult&&(identical(other.dishId, dishId) || other.dishId == dishId)&&(identical(other.dishName, dishName) || other.dishName == dishName)&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId)&&const DeepCollectionEquality().equals(other._changes, _changes)&&const DeepCollectionEquality().equals(other._updatedPantryItems, _updatedPantryItems)&&const DeepCollectionEquality().equals(other._depletedItemIds, _depletedItemIds)&&(identical(other.nearExpiryUsedCount, nearExpiryUsedCount) || other.nearExpiryUsedCount == nearExpiryUsedCount)&&(identical(other.wasteAvoidedGrams, wasteAvoidedGrams) || other.wasteAvoidedGrams == wasteAvoidedGrams));
}


@override
int get hashCode => Object.hash(runtimeType,dishId,dishName,sessionId,const DeepCollectionEquality().hash(_changes),const DeepCollectionEquality().hash(_updatedPantryItems),const DeepCollectionEquality().hash(_depletedItemIds),nearExpiryUsedCount,wasteAvoidedGrams);

@override
String toString() {
  return 'CookResult(dishId: $dishId, dishName: $dishName, sessionId: $sessionId, changes: $changes, updatedPantryItems: $updatedPantryItems, depletedItemIds: $depletedItemIds, nearExpiryUsedCount: $nearExpiryUsedCount, wasteAvoidedGrams: $wasteAvoidedGrams)';
}


}

/// @nodoc
abstract mixin class _$CookResultCopyWith<$Res> implements $CookResultCopyWith<$Res> {
  factory _$CookResultCopyWith(_CookResult value, $Res Function(_CookResult) _then) = __$CookResultCopyWithImpl;
@override @useResult
$Res call({
 String dishId, String dishName, String sessionId, List<PantryChange> changes, List<PantryItem> updatedPantryItems, List<String> depletedItemIds, int nearExpiryUsedCount, double wasteAvoidedGrams
});




}
/// @nodoc
class __$CookResultCopyWithImpl<$Res>
    implements _$CookResultCopyWith<$Res> {
  __$CookResultCopyWithImpl(this._self, this._then);

  final _CookResult _self;
  final $Res Function(_CookResult) _then;

/// Create a copy of CookResult
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? dishId = null,Object? dishName = null,Object? sessionId = null,Object? changes = null,Object? updatedPantryItems = null,Object? depletedItemIds = null,Object? nearExpiryUsedCount = null,Object? wasteAvoidedGrams = null,}) {
  return _then(_CookResult(
dishId: null == dishId ? _self.dishId : dishId // ignore: cast_nullable_to_non_nullable
as String,dishName: null == dishName ? _self.dishName : dishName // ignore: cast_nullable_to_non_nullable
as String,sessionId: null == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String,changes: null == changes ? _self._changes : changes // ignore: cast_nullable_to_non_nullable
as List<PantryChange>,updatedPantryItems: null == updatedPantryItems ? _self._updatedPantryItems : updatedPantryItems // ignore: cast_nullable_to_non_nullable
as List<PantryItem>,depletedItemIds: null == depletedItemIds ? _self._depletedItemIds : depletedItemIds // ignore: cast_nullable_to_non_nullable
as List<String>,nearExpiryUsedCount: null == nearExpiryUsedCount ? _self.nearExpiryUsedCount : nearExpiryUsedCount // ignore: cast_nullable_to_non_nullable
as int,wasteAvoidedGrams: null == wasteAvoidedGrams ? _self.wasteAvoidedGrams : wasteAvoidedGrams // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}

// dart format on
