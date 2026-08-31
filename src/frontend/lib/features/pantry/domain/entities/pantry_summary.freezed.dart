// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'pantry_summary.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$PantrySummary {

 int get totalCount; Map<StorageTier, int> get countByTier;/// Items to surface in "Cần dùng sớm" (already sorted by urgency).
 List<PantryItem> get nearExpiry;/// Ingredients used before their expiry date this period — the number shown
/// in the Home waste pill. (No money figure: scanning doesn't capture prices.)
 int get wasteReductionCount; double? get wasteAvoidedKg;
/// Create a copy of PantrySummary
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PantrySummaryCopyWith<PantrySummary> get copyWith => _$PantrySummaryCopyWithImpl<PantrySummary>(this as PantrySummary, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PantrySummary&&(identical(other.totalCount, totalCount) || other.totalCount == totalCount)&&const DeepCollectionEquality().equals(other.countByTier, countByTier)&&const DeepCollectionEquality().equals(other.nearExpiry, nearExpiry)&&(identical(other.wasteReductionCount, wasteReductionCount) || other.wasteReductionCount == wasteReductionCount)&&(identical(other.wasteAvoidedKg, wasteAvoidedKg) || other.wasteAvoidedKg == wasteAvoidedKg));
}


@override
int get hashCode => Object.hash(runtimeType,totalCount,const DeepCollectionEquality().hash(countByTier),const DeepCollectionEquality().hash(nearExpiry),wasteReductionCount,wasteAvoidedKg);

@override
String toString() {
  return 'PantrySummary(totalCount: $totalCount, countByTier: $countByTier, nearExpiry: $nearExpiry, wasteReductionCount: $wasteReductionCount, wasteAvoidedKg: $wasteAvoidedKg)';
}


}

/// @nodoc
abstract mixin class $PantrySummaryCopyWith<$Res>  {
  factory $PantrySummaryCopyWith(PantrySummary value, $Res Function(PantrySummary) _then) = _$PantrySummaryCopyWithImpl;
@useResult
$Res call({
 int totalCount, Map<StorageTier, int> countByTier, List<PantryItem> nearExpiry, int wasteReductionCount, double? wasteAvoidedKg
});




}
/// @nodoc
class _$PantrySummaryCopyWithImpl<$Res>
    implements $PantrySummaryCopyWith<$Res> {
  _$PantrySummaryCopyWithImpl(this._self, this._then);

  final PantrySummary _self;
  final $Res Function(PantrySummary) _then;

/// Create a copy of PantrySummary
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? totalCount = null,Object? countByTier = null,Object? nearExpiry = null,Object? wasteReductionCount = null,Object? wasteAvoidedKg = freezed,}) {
  return _then(_self.copyWith(
totalCount: null == totalCount ? _self.totalCount : totalCount // ignore: cast_nullable_to_non_nullable
as int,countByTier: null == countByTier ? _self.countByTier : countByTier // ignore: cast_nullable_to_non_nullable
as Map<StorageTier, int>,nearExpiry: null == nearExpiry ? _self.nearExpiry : nearExpiry // ignore: cast_nullable_to_non_nullable
as List<PantryItem>,wasteReductionCount: null == wasteReductionCount ? _self.wasteReductionCount : wasteReductionCount // ignore: cast_nullable_to_non_nullable
as int,wasteAvoidedKg: freezed == wasteAvoidedKg ? _self.wasteAvoidedKg : wasteAvoidedKg // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}

}


/// Adds pattern-matching-related methods to [PantrySummary].
extension PantrySummaryPatterns on PantrySummary {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PantrySummary value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PantrySummary() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PantrySummary value)  $default,){
final _that = this;
switch (_that) {
case _PantrySummary():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PantrySummary value)?  $default,){
final _that = this;
switch (_that) {
case _PantrySummary() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int totalCount,  Map<StorageTier, int> countByTier,  List<PantryItem> nearExpiry,  int wasteReductionCount,  double? wasteAvoidedKg)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PantrySummary() when $default != null:
return $default(_that.totalCount,_that.countByTier,_that.nearExpiry,_that.wasteReductionCount,_that.wasteAvoidedKg);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int totalCount,  Map<StorageTier, int> countByTier,  List<PantryItem> nearExpiry,  int wasteReductionCount,  double? wasteAvoidedKg)  $default,) {final _that = this;
switch (_that) {
case _PantrySummary():
return $default(_that.totalCount,_that.countByTier,_that.nearExpiry,_that.wasteReductionCount,_that.wasteAvoidedKg);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int totalCount,  Map<StorageTier, int> countByTier,  List<PantryItem> nearExpiry,  int wasteReductionCount,  double? wasteAvoidedKg)?  $default,) {final _that = this;
switch (_that) {
case _PantrySummary() when $default != null:
return $default(_that.totalCount,_that.countByTier,_that.nearExpiry,_that.wasteReductionCount,_that.wasteAvoidedKg);case _:
  return null;

}
}

}

/// @nodoc


class _PantrySummary extends PantrySummary {
  const _PantrySummary({required this.totalCount, required final  Map<StorageTier, int> countByTier, required final  List<PantryItem> nearExpiry, required this.wasteReductionCount, this.wasteAvoidedKg}): _countByTier = countByTier,_nearExpiry = nearExpiry,super._();
  

@override final  int totalCount;
 final  Map<StorageTier, int> _countByTier;
@override Map<StorageTier, int> get countByTier {
  if (_countByTier is EqualUnmodifiableMapView) return _countByTier;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_countByTier);
}

/// Items to surface in "Cần dùng sớm" (already sorted by urgency).
 final  List<PantryItem> _nearExpiry;
/// Items to surface in "Cần dùng sớm" (already sorted by urgency).
@override List<PantryItem> get nearExpiry {
  if (_nearExpiry is EqualUnmodifiableListView) return _nearExpiry;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_nearExpiry);
}

/// Ingredients used before their expiry date this period — the number shown
/// in the Home waste pill. (No money figure: scanning doesn't capture prices.)
@override final  int wasteReductionCount;
@override final  double? wasteAvoidedKg;

/// Create a copy of PantrySummary
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PantrySummaryCopyWith<_PantrySummary> get copyWith => __$PantrySummaryCopyWithImpl<_PantrySummary>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _PantrySummary&&(identical(other.totalCount, totalCount) || other.totalCount == totalCount)&&const DeepCollectionEquality().equals(other._countByTier, _countByTier)&&const DeepCollectionEquality().equals(other._nearExpiry, _nearExpiry)&&(identical(other.wasteReductionCount, wasteReductionCount) || other.wasteReductionCount == wasteReductionCount)&&(identical(other.wasteAvoidedKg, wasteAvoidedKg) || other.wasteAvoidedKg == wasteAvoidedKg));
}


@override
int get hashCode => Object.hash(runtimeType,totalCount,const DeepCollectionEquality().hash(_countByTier),const DeepCollectionEquality().hash(_nearExpiry),wasteReductionCount,wasteAvoidedKg);

@override
String toString() {
  return 'PantrySummary(totalCount: $totalCount, countByTier: $countByTier, nearExpiry: $nearExpiry, wasteReductionCount: $wasteReductionCount, wasteAvoidedKg: $wasteAvoidedKg)';
}


}

/// @nodoc
abstract mixin class _$PantrySummaryCopyWith<$Res> implements $PantrySummaryCopyWith<$Res> {
  factory _$PantrySummaryCopyWith(_PantrySummary value, $Res Function(_PantrySummary) _then) = __$PantrySummaryCopyWithImpl;
@override @useResult
$Res call({
 int totalCount, Map<StorageTier, int> countByTier, List<PantryItem> nearExpiry, int wasteReductionCount, double? wasteAvoidedKg
});




}
/// @nodoc
class __$PantrySummaryCopyWithImpl<$Res>
    implements _$PantrySummaryCopyWith<$Res> {
  __$PantrySummaryCopyWithImpl(this._self, this._then);

  final _PantrySummary _self;
  final $Res Function(_PantrySummary) _then;

/// Create a copy of PantrySummary
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? totalCount = null,Object? countByTier = null,Object? nearExpiry = null,Object? wasteReductionCount = null,Object? wasteAvoidedKg = freezed,}) {
  return _then(_PantrySummary(
totalCount: null == totalCount ? _self.totalCount : totalCount // ignore: cast_nullable_to_non_nullable
as int,countByTier: null == countByTier ? _self._countByTier : countByTier // ignore: cast_nullable_to_non_nullable
as Map<StorageTier, int>,nearExpiry: null == nearExpiry ? _self._nearExpiry : nearExpiry // ignore: cast_nullable_to_non_nullable
as List<PantryItem>,wasteReductionCount: null == wasteReductionCount ? _self.wasteReductionCount : wasteReductionCount // ignore: cast_nullable_to_non_nullable
as int,wasteAvoidedKg: freezed == wasteAvoidedKg ? _self.wasteAvoidedKg : wasteAvoidedKg // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}


}

// dart format on
