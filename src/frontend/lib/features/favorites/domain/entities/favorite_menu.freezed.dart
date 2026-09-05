// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'favorite_menu.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$FavoriteMenu {

 String get id; String get name; String? get description; DateTime get createdAt; DateTime get updatedAt; int get itemCount;
/// Create a copy of FavoriteMenu
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FavoriteMenuCopyWith<FavoriteMenu> get copyWith => _$FavoriteMenuCopyWithImpl<FavoriteMenu>(this as FavoriteMenu, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FavoriteMenu&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.itemCount, itemCount) || other.itemCount == itemCount));
}


@override
int get hashCode => Object.hash(runtimeType,id,name,description,createdAt,updatedAt,itemCount);

@override
String toString() {
  return 'FavoriteMenu(id: $id, name: $name, description: $description, createdAt: $createdAt, updatedAt: $updatedAt, itemCount: $itemCount)';
}


}

/// @nodoc
abstract mixin class $FavoriteMenuCopyWith<$Res>  {
  factory $FavoriteMenuCopyWith(FavoriteMenu value, $Res Function(FavoriteMenu) _then) = _$FavoriteMenuCopyWithImpl;
@useResult
$Res call({
 String id, String name, String? description, DateTime createdAt, DateTime updatedAt, int itemCount
});




}
/// @nodoc
class _$FavoriteMenuCopyWithImpl<$Res>
    implements $FavoriteMenuCopyWith<$Res> {
  _$FavoriteMenuCopyWithImpl(this._self, this._then);

  final FavoriteMenu _self;
  final $Res Function(FavoriteMenu) _then;

/// Create a copy of FavoriteMenu
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? createdAt = null,Object? updatedAt = null,Object? itemCount = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,itemCount: null == itemCount ? _self.itemCount : itemCount // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [FavoriteMenu].
extension FavoriteMenuPatterns on FavoriteMenu {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FavoriteMenu value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FavoriteMenu() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FavoriteMenu value)  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenu():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FavoriteMenu value)?  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenu() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String? description,  DateTime createdAt,  DateTime updatedAt,  int itemCount)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FavoriteMenu() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt,_that.itemCount);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String? description,  DateTime createdAt,  DateTime updatedAt,  int itemCount)  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenu():
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt,_that.itemCount);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String? description,  DateTime createdAt,  DateTime updatedAt,  int itemCount)?  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenu() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt,_that.itemCount);case _:
  return null;

}
}

}

/// @nodoc


class _FavoriteMenu implements FavoriteMenu {
  const _FavoriteMenu({required this.id, required this.name, this.description, required this.createdAt, required this.updatedAt, this.itemCount = 0});
  

@override final  String id;
@override final  String name;
@override final  String? description;
@override final  DateTime createdAt;
@override final  DateTime updatedAt;
@override@JsonKey() final  int itemCount;

/// Create a copy of FavoriteMenu
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FavoriteMenuCopyWith<_FavoriteMenu> get copyWith => __$FavoriteMenuCopyWithImpl<_FavoriteMenu>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FavoriteMenu&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.itemCount, itemCount) || other.itemCount == itemCount));
}


@override
int get hashCode => Object.hash(runtimeType,id,name,description,createdAt,updatedAt,itemCount);

@override
String toString() {
  return 'FavoriteMenu(id: $id, name: $name, description: $description, createdAt: $createdAt, updatedAt: $updatedAt, itemCount: $itemCount)';
}


}

/// @nodoc
abstract mixin class _$FavoriteMenuCopyWith<$Res> implements $FavoriteMenuCopyWith<$Res> {
  factory _$FavoriteMenuCopyWith(_FavoriteMenu value, $Res Function(_FavoriteMenu) _then) = __$FavoriteMenuCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String? description, DateTime createdAt, DateTime updatedAt, int itemCount
});




}
/// @nodoc
class __$FavoriteMenuCopyWithImpl<$Res>
    implements _$FavoriteMenuCopyWith<$Res> {
  __$FavoriteMenuCopyWithImpl(this._self, this._then);

  final _FavoriteMenu _self;
  final $Res Function(_FavoriteMenu) _then;

/// Create a copy of FavoriteMenu
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? createdAt = null,Object? updatedAt = null,Object? itemCount = null,}) {
  return _then(_FavoriteMenu(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,itemCount: null == itemCount ? _self.itemCount : itemCount // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

/// @nodoc
mixin _$FavoriteMenuItem {

 String get id; String get recipeId; String get recipeName; String get recipeDescription; String? get mediaUrl; DateTime get createdAt;
/// Create a copy of FavoriteMenuItem
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FavoriteMenuItemCopyWith<FavoriteMenuItem> get copyWith => _$FavoriteMenuItemCopyWithImpl<FavoriteMenuItem>(this as FavoriteMenuItem, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FavoriteMenuItem&&(identical(other.id, id) || other.id == id)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.recipeDescription, recipeDescription) || other.recipeDescription == recipeDescription)&&(identical(other.mediaUrl, mediaUrl) || other.mediaUrl == mediaUrl)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}


@override
int get hashCode => Object.hash(runtimeType,id,recipeId,recipeName,recipeDescription,mediaUrl,createdAt);

@override
String toString() {
  return 'FavoriteMenuItem(id: $id, recipeId: $recipeId, recipeName: $recipeName, recipeDescription: $recipeDescription, mediaUrl: $mediaUrl, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $FavoriteMenuItemCopyWith<$Res>  {
  factory $FavoriteMenuItemCopyWith(FavoriteMenuItem value, $Res Function(FavoriteMenuItem) _then) = _$FavoriteMenuItemCopyWithImpl;
@useResult
$Res call({
 String id, String recipeId, String recipeName, String recipeDescription, String? mediaUrl, DateTime createdAt
});




}
/// @nodoc
class _$FavoriteMenuItemCopyWithImpl<$Res>
    implements $FavoriteMenuItemCopyWith<$Res> {
  _$FavoriteMenuItemCopyWithImpl(this._self, this._then);

  final FavoriteMenuItem _self;
  final $Res Function(FavoriteMenuItem) _then;

/// Create a copy of FavoriteMenuItem
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? recipeId = null,Object? recipeName = null,Object? recipeDescription = null,Object? mediaUrl = freezed,Object? createdAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,recipeDescription: null == recipeDescription ? _self.recipeDescription : recipeDescription // ignore: cast_nullable_to_non_nullable
as String,mediaUrl: freezed == mediaUrl ? _self.mediaUrl : mediaUrl // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [FavoriteMenuItem].
extension FavoriteMenuItemPatterns on FavoriteMenuItem {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FavoriteMenuItem value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FavoriteMenuItem() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FavoriteMenuItem value)  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuItem():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FavoriteMenuItem value)?  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuItem() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String recipeId,  String recipeName,  String recipeDescription,  String? mediaUrl,  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FavoriteMenuItem() when $default != null:
return $default(_that.id,_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String recipeId,  String recipeName,  String recipeDescription,  String? mediaUrl,  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuItem():
return $default(_that.id,_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String recipeId,  String recipeName,  String recipeDescription,  String? mediaUrl,  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuItem() when $default != null:
return $default(_that.id,_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc


class _FavoriteMenuItem implements FavoriteMenuItem {
  const _FavoriteMenuItem({required this.id, required this.recipeId, required this.recipeName, this.recipeDescription = '', this.mediaUrl, required this.createdAt});
  

@override final  String id;
@override final  String recipeId;
@override final  String recipeName;
@override@JsonKey() final  String recipeDescription;
@override final  String? mediaUrl;
@override final  DateTime createdAt;

/// Create a copy of FavoriteMenuItem
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FavoriteMenuItemCopyWith<_FavoriteMenuItem> get copyWith => __$FavoriteMenuItemCopyWithImpl<_FavoriteMenuItem>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FavoriteMenuItem&&(identical(other.id, id) || other.id == id)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.recipeDescription, recipeDescription) || other.recipeDescription == recipeDescription)&&(identical(other.mediaUrl, mediaUrl) || other.mediaUrl == mediaUrl)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}


@override
int get hashCode => Object.hash(runtimeType,id,recipeId,recipeName,recipeDescription,mediaUrl,createdAt);

@override
String toString() {
  return 'FavoriteMenuItem(id: $id, recipeId: $recipeId, recipeName: $recipeName, recipeDescription: $recipeDescription, mediaUrl: $mediaUrl, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$FavoriteMenuItemCopyWith<$Res> implements $FavoriteMenuItemCopyWith<$Res> {
  factory _$FavoriteMenuItemCopyWith(_FavoriteMenuItem value, $Res Function(_FavoriteMenuItem) _then) = __$FavoriteMenuItemCopyWithImpl;
@override @useResult
$Res call({
 String id, String recipeId, String recipeName, String recipeDescription, String? mediaUrl, DateTime createdAt
});




}
/// @nodoc
class __$FavoriteMenuItemCopyWithImpl<$Res>
    implements _$FavoriteMenuItemCopyWith<$Res> {
  __$FavoriteMenuItemCopyWithImpl(this._self, this._then);

  final _FavoriteMenuItem _self;
  final $Res Function(_FavoriteMenuItem) _then;

/// Create a copy of FavoriteMenuItem
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? recipeId = null,Object? recipeName = null,Object? recipeDescription = null,Object? mediaUrl = freezed,Object? createdAt = null,}) {
  return _then(_FavoriteMenuItem(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,recipeDescription: null == recipeDescription ? _self.recipeDescription : recipeDescription // ignore: cast_nullable_to_non_nullable
as String,mediaUrl: freezed == mediaUrl ? _self.mediaUrl : mediaUrl // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}

/// @nodoc
mixin _$FavoriteMenuDetail {

 String get id; String get name; String? get description; DateTime get createdAt; DateTime get updatedAt; List<FavoriteMenuItem> get items;
/// Create a copy of FavoriteMenuDetail
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FavoriteMenuDetailCopyWith<FavoriteMenuDetail> get copyWith => _$FavoriteMenuDetailCopyWithImpl<FavoriteMenuDetail>(this as FavoriteMenuDetail, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FavoriteMenuDetail&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&const DeepCollectionEquality().equals(other.items, items));
}


@override
int get hashCode => Object.hash(runtimeType,id,name,description,createdAt,updatedAt,const DeepCollectionEquality().hash(items));

@override
String toString() {
  return 'FavoriteMenuDetail(id: $id, name: $name, description: $description, createdAt: $createdAt, updatedAt: $updatedAt, items: $items)';
}


}

/// @nodoc
abstract mixin class $FavoriteMenuDetailCopyWith<$Res>  {
  factory $FavoriteMenuDetailCopyWith(FavoriteMenuDetail value, $Res Function(FavoriteMenuDetail) _then) = _$FavoriteMenuDetailCopyWithImpl;
@useResult
$Res call({
 String id, String name, String? description, DateTime createdAt, DateTime updatedAt, List<FavoriteMenuItem> items
});




}
/// @nodoc
class _$FavoriteMenuDetailCopyWithImpl<$Res>
    implements $FavoriteMenuDetailCopyWith<$Res> {
  _$FavoriteMenuDetailCopyWithImpl(this._self, this._then);

  final FavoriteMenuDetail _self;
  final $Res Function(FavoriteMenuDetail) _then;

/// Create a copy of FavoriteMenuDetail
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? createdAt = null,Object? updatedAt = null,Object? items = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<FavoriteMenuItem>,
  ));
}

}


/// Adds pattern-matching-related methods to [FavoriteMenuDetail].
extension FavoriteMenuDetailPatterns on FavoriteMenuDetail {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FavoriteMenuDetail value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FavoriteMenuDetail() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FavoriteMenuDetail value)  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuDetail():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FavoriteMenuDetail value)?  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuDetail() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String? description,  DateTime createdAt,  DateTime updatedAt,  List<FavoriteMenuItem> items)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FavoriteMenuDetail() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt,_that.items);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String? description,  DateTime createdAt,  DateTime updatedAt,  List<FavoriteMenuItem> items)  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuDetail():
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt,_that.items);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String? description,  DateTime createdAt,  DateTime updatedAt,  List<FavoriteMenuItem> items)?  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuDetail() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt,_that.items);case _:
  return null;

}
}

}

/// @nodoc


class _FavoriteMenuDetail implements FavoriteMenuDetail {
  const _FavoriteMenuDetail({required this.id, required this.name, this.description, required this.createdAt, required this.updatedAt, final  List<FavoriteMenuItem> items = const <FavoriteMenuItem>[]}): _items = items;
  

@override final  String id;
@override final  String name;
@override final  String? description;
@override final  DateTime createdAt;
@override final  DateTime updatedAt;
 final  List<FavoriteMenuItem> _items;
@override@JsonKey() List<FavoriteMenuItem> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


/// Create a copy of FavoriteMenuDetail
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FavoriteMenuDetailCopyWith<_FavoriteMenuDetail> get copyWith => __$FavoriteMenuDetailCopyWithImpl<_FavoriteMenuDetail>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FavoriteMenuDetail&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&const DeepCollectionEquality().equals(other._items, _items));
}


@override
int get hashCode => Object.hash(runtimeType,id,name,description,createdAt,updatedAt,const DeepCollectionEquality().hash(_items));

@override
String toString() {
  return 'FavoriteMenuDetail(id: $id, name: $name, description: $description, createdAt: $createdAt, updatedAt: $updatedAt, items: $items)';
}


}

/// @nodoc
abstract mixin class _$FavoriteMenuDetailCopyWith<$Res> implements $FavoriteMenuDetailCopyWith<$Res> {
  factory _$FavoriteMenuDetailCopyWith(_FavoriteMenuDetail value, $Res Function(_FavoriteMenuDetail) _then) = __$FavoriteMenuDetailCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String? description, DateTime createdAt, DateTime updatedAt, List<FavoriteMenuItem> items
});




}
/// @nodoc
class __$FavoriteMenuDetailCopyWithImpl<$Res>
    implements _$FavoriteMenuDetailCopyWith<$Res> {
  __$FavoriteMenuDetailCopyWithImpl(this._self, this._then);

  final _FavoriteMenuDetail _self;
  final $Res Function(_FavoriteMenuDetail) _then;

/// Create a copy of FavoriteMenuDetail
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? createdAt = null,Object? updatedAt = null,Object? items = null,}) {
  return _then(_FavoriteMenuDetail(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<FavoriteMenuItem>,
  ));
}


}

// dart format on
