// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'favorite_recipe.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$FavoriteRecipe {

 String get recipeId; String get recipeName; String get recipeDescription; String? get mediaUrl; DateTime get createdAt;
/// Create a copy of FavoriteRecipe
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FavoriteRecipeCopyWith<FavoriteRecipe> get copyWith => _$FavoriteRecipeCopyWithImpl<FavoriteRecipe>(this as FavoriteRecipe, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FavoriteRecipe&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.recipeDescription, recipeDescription) || other.recipeDescription == recipeDescription)&&(identical(other.mediaUrl, mediaUrl) || other.mediaUrl == mediaUrl)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}


@override
int get hashCode => Object.hash(runtimeType,recipeId,recipeName,recipeDescription,mediaUrl,createdAt);

@override
String toString() {
  return 'FavoriteRecipe(recipeId: $recipeId, recipeName: $recipeName, recipeDescription: $recipeDescription, mediaUrl: $mediaUrl, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $FavoriteRecipeCopyWith<$Res>  {
  factory $FavoriteRecipeCopyWith(FavoriteRecipe value, $Res Function(FavoriteRecipe) _then) = _$FavoriteRecipeCopyWithImpl;
@useResult
$Res call({
 String recipeId, String recipeName, String recipeDescription, String? mediaUrl, DateTime createdAt
});




}
/// @nodoc
class _$FavoriteRecipeCopyWithImpl<$Res>
    implements $FavoriteRecipeCopyWith<$Res> {
  _$FavoriteRecipeCopyWithImpl(this._self, this._then);

  final FavoriteRecipe _self;
  final $Res Function(FavoriteRecipe) _then;

/// Create a copy of FavoriteRecipe
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeId = null,Object? recipeName = null,Object? recipeDescription = null,Object? mediaUrl = freezed,Object? createdAt = null,}) {
  return _then(_self.copyWith(
recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,recipeDescription: null == recipeDescription ? _self.recipeDescription : recipeDescription // ignore: cast_nullable_to_non_nullable
as String,mediaUrl: freezed == mediaUrl ? _self.mediaUrl : mediaUrl // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [FavoriteRecipe].
extension FavoriteRecipePatterns on FavoriteRecipe {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FavoriteRecipe value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FavoriteRecipe() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FavoriteRecipe value)  $default,){
final _that = this;
switch (_that) {
case _FavoriteRecipe():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FavoriteRecipe value)?  $default,){
final _that = this;
switch (_that) {
case _FavoriteRecipe() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String recipeId,  String recipeName,  String recipeDescription,  String? mediaUrl,  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FavoriteRecipe() when $default != null:
return $default(_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String recipeId,  String recipeName,  String recipeDescription,  String? mediaUrl,  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _FavoriteRecipe():
return $default(_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String recipeId,  String recipeName,  String recipeDescription,  String? mediaUrl,  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _FavoriteRecipe() when $default != null:
return $default(_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc


class _FavoriteRecipe implements FavoriteRecipe {
  const _FavoriteRecipe({required this.recipeId, required this.recipeName, this.recipeDescription = '', this.mediaUrl, required this.createdAt});
  

@override final  String recipeId;
@override final  String recipeName;
@override@JsonKey() final  String recipeDescription;
@override final  String? mediaUrl;
@override final  DateTime createdAt;

/// Create a copy of FavoriteRecipe
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FavoriteRecipeCopyWith<_FavoriteRecipe> get copyWith => __$FavoriteRecipeCopyWithImpl<_FavoriteRecipe>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FavoriteRecipe&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.recipeDescription, recipeDescription) || other.recipeDescription == recipeDescription)&&(identical(other.mediaUrl, mediaUrl) || other.mediaUrl == mediaUrl)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}


@override
int get hashCode => Object.hash(runtimeType,recipeId,recipeName,recipeDescription,mediaUrl,createdAt);

@override
String toString() {
  return 'FavoriteRecipe(recipeId: $recipeId, recipeName: $recipeName, recipeDescription: $recipeDescription, mediaUrl: $mediaUrl, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$FavoriteRecipeCopyWith<$Res> implements $FavoriteRecipeCopyWith<$Res> {
  factory _$FavoriteRecipeCopyWith(_FavoriteRecipe value, $Res Function(_FavoriteRecipe) _then) = __$FavoriteRecipeCopyWithImpl;
@override @useResult
$Res call({
 String recipeId, String recipeName, String recipeDescription, String? mediaUrl, DateTime createdAt
});




}
/// @nodoc
class __$FavoriteRecipeCopyWithImpl<$Res>
    implements _$FavoriteRecipeCopyWith<$Res> {
  __$FavoriteRecipeCopyWithImpl(this._self, this._then);

  final _FavoriteRecipe _self;
  final $Res Function(_FavoriteRecipe) _then;

/// Create a copy of FavoriteRecipe
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeId = null,Object? recipeName = null,Object? recipeDescription = null,Object? mediaUrl = freezed,Object? createdAt = null,}) {
  return _then(_FavoriteRecipe(
recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,recipeDescription: null == recipeDescription ? _self.recipeDescription : recipeDescription // ignore: cast_nullable_to_non_nullable
as String,mediaUrl: freezed == mediaUrl ? _self.mediaUrl : mediaUrl // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}

// dart format on
