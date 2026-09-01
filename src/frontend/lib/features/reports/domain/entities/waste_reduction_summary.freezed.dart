// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'waste_reduction_summary.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$WasteReductionBar {

 String get label; int get value;
/// Create a copy of WasteReductionBar
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WasteReductionBarCopyWith<WasteReductionBar> get copyWith => _$WasteReductionBarCopyWithImpl<WasteReductionBar>(this as WasteReductionBar, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WasteReductionBar&&(identical(other.label, label) || other.label == label)&&(identical(other.value, value) || other.value == value));
}


@override
int get hashCode => Object.hash(runtimeType,label,value);

@override
String toString() {
  return 'WasteReductionBar(label: $label, value: $value)';
}


}

/// @nodoc
abstract mixin class $WasteReductionBarCopyWith<$Res>  {
  factory $WasteReductionBarCopyWith(WasteReductionBar value, $Res Function(WasteReductionBar) _then) = _$WasteReductionBarCopyWithImpl;
@useResult
$Res call({
 String label, int value
});




}
/// @nodoc
class _$WasteReductionBarCopyWithImpl<$Res>
    implements $WasteReductionBarCopyWith<$Res> {
  _$WasteReductionBarCopyWithImpl(this._self, this._then);

  final WasteReductionBar _self;
  final $Res Function(WasteReductionBar) _then;

/// Create a copy of WasteReductionBar
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? label = null,Object? value = null,}) {
  return _then(_self.copyWith(
label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,value: null == value ? _self.value : value // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [WasteReductionBar].
extension WasteReductionBarPatterns on WasteReductionBar {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WasteReductionBar value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WasteReductionBar() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WasteReductionBar value)  $default,){
final _that = this;
switch (_that) {
case _WasteReductionBar():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WasteReductionBar value)?  $default,){
final _that = this;
switch (_that) {
case _WasteReductionBar() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String label,  int value)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WasteReductionBar() when $default != null:
return $default(_that.label,_that.value);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String label,  int value)  $default,) {final _that = this;
switch (_that) {
case _WasteReductionBar():
return $default(_that.label,_that.value);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String label,  int value)?  $default,) {final _that = this;
switch (_that) {
case _WasteReductionBar() when $default != null:
return $default(_that.label,_that.value);case _:
  return null;

}
}

}

/// @nodoc


class _WasteReductionBar implements WasteReductionBar {
  const _WasteReductionBar({required this.label, required this.value});
  

@override final  String label;
@override final  int value;

/// Create a copy of WasteReductionBar
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WasteReductionBarCopyWith<_WasteReductionBar> get copyWith => __$WasteReductionBarCopyWithImpl<_WasteReductionBar>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WasteReductionBar&&(identical(other.label, label) || other.label == label)&&(identical(other.value, value) || other.value == value));
}


@override
int get hashCode => Object.hash(runtimeType,label,value);

@override
String toString() {
  return 'WasteReductionBar(label: $label, value: $value)';
}


}

/// @nodoc
abstract mixin class _$WasteReductionBarCopyWith<$Res> implements $WasteReductionBarCopyWith<$Res> {
  factory _$WasteReductionBarCopyWith(_WasteReductionBar value, $Res Function(_WasteReductionBar) _then) = __$WasteReductionBarCopyWithImpl;
@override @useResult
$Res call({
 String label, int value
});




}
/// @nodoc
class __$WasteReductionBarCopyWithImpl<$Res>
    implements _$WasteReductionBarCopyWith<$Res> {
  __$WasteReductionBarCopyWithImpl(this._self, this._then);

  final _WasteReductionBar _self;
  final $Res Function(_WasteReductionBar) _then;

/// Create a copy of WasteReductionBar
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? label = null,Object? value = null,}) {
  return _then(_WasteReductionBar(
label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,value: null == value ? _self.value : value // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

/// @nodoc
mixin _$WasteReductionCategory {

 String get category; int get count; int get colorValue;
/// Create a copy of WasteReductionCategory
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WasteReductionCategoryCopyWith<WasteReductionCategory> get copyWith => _$WasteReductionCategoryCopyWithImpl<WasteReductionCategory>(this as WasteReductionCategory, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WasteReductionCategory&&(identical(other.category, category) || other.category == category)&&(identical(other.count, count) || other.count == count)&&(identical(other.colorValue, colorValue) || other.colorValue == colorValue));
}


@override
int get hashCode => Object.hash(runtimeType,category,count,colorValue);

@override
String toString() {
  return 'WasteReductionCategory(category: $category, count: $count, colorValue: $colorValue)';
}


}

/// @nodoc
abstract mixin class $WasteReductionCategoryCopyWith<$Res>  {
  factory $WasteReductionCategoryCopyWith(WasteReductionCategory value, $Res Function(WasteReductionCategory) _then) = _$WasteReductionCategoryCopyWithImpl;
@useResult
$Res call({
 String category, int count, int colorValue
});




}
/// @nodoc
class _$WasteReductionCategoryCopyWithImpl<$Res>
    implements $WasteReductionCategoryCopyWith<$Res> {
  _$WasteReductionCategoryCopyWithImpl(this._self, this._then);

  final WasteReductionCategory _self;
  final $Res Function(WasteReductionCategory) _then;

/// Create a copy of WasteReductionCategory
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? category = null,Object? count = null,Object? colorValue = null,}) {
  return _then(_self.copyWith(
category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,count: null == count ? _self.count : count // ignore: cast_nullable_to_non_nullable
as int,colorValue: null == colorValue ? _self.colorValue : colorValue // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [WasteReductionCategory].
extension WasteReductionCategoryPatterns on WasteReductionCategory {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WasteReductionCategory value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WasteReductionCategory() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WasteReductionCategory value)  $default,){
final _that = this;
switch (_that) {
case _WasteReductionCategory():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WasteReductionCategory value)?  $default,){
final _that = this;
switch (_that) {
case _WasteReductionCategory() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String category,  int count,  int colorValue)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WasteReductionCategory() when $default != null:
return $default(_that.category,_that.count,_that.colorValue);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String category,  int count,  int colorValue)  $default,) {final _that = this;
switch (_that) {
case _WasteReductionCategory():
return $default(_that.category,_that.count,_that.colorValue);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String category,  int count,  int colorValue)?  $default,) {final _that = this;
switch (_that) {
case _WasteReductionCategory() when $default != null:
return $default(_that.category,_that.count,_that.colorValue);case _:
  return null;

}
}

}

/// @nodoc


class _WasteReductionCategory implements WasteReductionCategory {
  const _WasteReductionCategory({required this.category, required this.count, required this.colorValue});
  

@override final  String category;
@override final  int count;
@override final  int colorValue;

/// Create a copy of WasteReductionCategory
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WasteReductionCategoryCopyWith<_WasteReductionCategory> get copyWith => __$WasteReductionCategoryCopyWithImpl<_WasteReductionCategory>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WasteReductionCategory&&(identical(other.category, category) || other.category == category)&&(identical(other.count, count) || other.count == count)&&(identical(other.colorValue, colorValue) || other.colorValue == colorValue));
}


@override
int get hashCode => Object.hash(runtimeType,category,count,colorValue);

@override
String toString() {
  return 'WasteReductionCategory(category: $category, count: $count, colorValue: $colorValue)';
}


}

/// @nodoc
abstract mixin class _$WasteReductionCategoryCopyWith<$Res> implements $WasteReductionCategoryCopyWith<$Res> {
  factory _$WasteReductionCategoryCopyWith(_WasteReductionCategory value, $Res Function(_WasteReductionCategory) _then) = __$WasteReductionCategoryCopyWithImpl;
@override @useResult
$Res call({
 String category, int count, int colorValue
});




}
/// @nodoc
class __$WasteReductionCategoryCopyWithImpl<$Res>
    implements _$WasteReductionCategoryCopyWith<$Res> {
  __$WasteReductionCategoryCopyWithImpl(this._self, this._then);

  final _WasteReductionCategory _self;
  final $Res Function(_WasteReductionCategory) _then;

/// Create a copy of WasteReductionCategory
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? category = null,Object? count = null,Object? colorValue = null,}) {
  return _then(_WasteReductionCategory(
category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,count: null == count ? _self.count : count // ignore: cast_nullable_to_non_nullable
as int,colorValue: null == colorValue ? _self.colorValue : colorValue // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

/// @nodoc
mixin _$WasteReductionSummary {

 ReportPeriod get period; String get periodLabel; int get itemsUsedBeforeExpiry; double get wasteAvoidedKg; int get dishesCooked; List<WasteReductionBar> get weeklyBars; List<WasteReductionCategory> get byCategory;
/// Create a copy of WasteReductionSummary
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WasteReductionSummaryCopyWith<WasteReductionSummary> get copyWith => _$WasteReductionSummaryCopyWithImpl<WasteReductionSummary>(this as WasteReductionSummary, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WasteReductionSummary&&(identical(other.period, period) || other.period == period)&&(identical(other.periodLabel, periodLabel) || other.periodLabel == periodLabel)&&(identical(other.itemsUsedBeforeExpiry, itemsUsedBeforeExpiry) || other.itemsUsedBeforeExpiry == itemsUsedBeforeExpiry)&&(identical(other.wasteAvoidedKg, wasteAvoidedKg) || other.wasteAvoidedKg == wasteAvoidedKg)&&(identical(other.dishesCooked, dishesCooked) || other.dishesCooked == dishesCooked)&&const DeepCollectionEquality().equals(other.weeklyBars, weeklyBars)&&const DeepCollectionEquality().equals(other.byCategory, byCategory));
}


@override
int get hashCode => Object.hash(runtimeType,period,periodLabel,itemsUsedBeforeExpiry,wasteAvoidedKg,dishesCooked,const DeepCollectionEquality().hash(weeklyBars),const DeepCollectionEquality().hash(byCategory));

@override
String toString() {
  return 'WasteReductionSummary(period: $period, periodLabel: $periodLabel, itemsUsedBeforeExpiry: $itemsUsedBeforeExpiry, wasteAvoidedKg: $wasteAvoidedKg, dishesCooked: $dishesCooked, weeklyBars: $weeklyBars, byCategory: $byCategory)';
}


}

/// @nodoc
abstract mixin class $WasteReductionSummaryCopyWith<$Res>  {
  factory $WasteReductionSummaryCopyWith(WasteReductionSummary value, $Res Function(WasteReductionSummary) _then) = _$WasteReductionSummaryCopyWithImpl;
@useResult
$Res call({
 ReportPeriod period, String periodLabel, int itemsUsedBeforeExpiry, double wasteAvoidedKg, int dishesCooked, List<WasteReductionBar> weeklyBars, List<WasteReductionCategory> byCategory
});




}
/// @nodoc
class _$WasteReductionSummaryCopyWithImpl<$Res>
    implements $WasteReductionSummaryCopyWith<$Res> {
  _$WasteReductionSummaryCopyWithImpl(this._self, this._then);

  final WasteReductionSummary _self;
  final $Res Function(WasteReductionSummary) _then;

/// Create a copy of WasteReductionSummary
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? period = null,Object? periodLabel = null,Object? itemsUsedBeforeExpiry = null,Object? wasteAvoidedKg = null,Object? dishesCooked = null,Object? weeklyBars = null,Object? byCategory = null,}) {
  return _then(_self.copyWith(
period: null == period ? _self.period : period // ignore: cast_nullable_to_non_nullable
as ReportPeriod,periodLabel: null == periodLabel ? _self.periodLabel : periodLabel // ignore: cast_nullable_to_non_nullable
as String,itemsUsedBeforeExpiry: null == itemsUsedBeforeExpiry ? _self.itemsUsedBeforeExpiry : itemsUsedBeforeExpiry // ignore: cast_nullable_to_non_nullable
as int,wasteAvoidedKg: null == wasteAvoidedKg ? _self.wasteAvoidedKg : wasteAvoidedKg // ignore: cast_nullable_to_non_nullable
as double,dishesCooked: null == dishesCooked ? _self.dishesCooked : dishesCooked // ignore: cast_nullable_to_non_nullable
as int,weeklyBars: null == weeklyBars ? _self.weeklyBars : weeklyBars // ignore: cast_nullable_to_non_nullable
as List<WasteReductionBar>,byCategory: null == byCategory ? _self.byCategory : byCategory // ignore: cast_nullable_to_non_nullable
as List<WasteReductionCategory>,
  ));
}

}


/// Adds pattern-matching-related methods to [WasteReductionSummary].
extension WasteReductionSummaryPatterns on WasteReductionSummary {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WasteReductionSummary value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WasteReductionSummary() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WasteReductionSummary value)  $default,){
final _that = this;
switch (_that) {
case _WasteReductionSummary():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WasteReductionSummary value)?  $default,){
final _that = this;
switch (_that) {
case _WasteReductionSummary() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( ReportPeriod period,  String periodLabel,  int itemsUsedBeforeExpiry,  double wasteAvoidedKg,  int dishesCooked,  List<WasteReductionBar> weeklyBars,  List<WasteReductionCategory> byCategory)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WasteReductionSummary() when $default != null:
return $default(_that.period,_that.periodLabel,_that.itemsUsedBeforeExpiry,_that.wasteAvoidedKg,_that.dishesCooked,_that.weeklyBars,_that.byCategory);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( ReportPeriod period,  String periodLabel,  int itemsUsedBeforeExpiry,  double wasteAvoidedKg,  int dishesCooked,  List<WasteReductionBar> weeklyBars,  List<WasteReductionCategory> byCategory)  $default,) {final _that = this;
switch (_that) {
case _WasteReductionSummary():
return $default(_that.period,_that.periodLabel,_that.itemsUsedBeforeExpiry,_that.wasteAvoidedKg,_that.dishesCooked,_that.weeklyBars,_that.byCategory);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( ReportPeriod period,  String periodLabel,  int itemsUsedBeforeExpiry,  double wasteAvoidedKg,  int dishesCooked,  List<WasteReductionBar> weeklyBars,  List<WasteReductionCategory> byCategory)?  $default,) {final _that = this;
switch (_that) {
case _WasteReductionSummary() when $default != null:
return $default(_that.period,_that.periodLabel,_that.itemsUsedBeforeExpiry,_that.wasteAvoidedKg,_that.dishesCooked,_that.weeklyBars,_that.byCategory);case _:
  return null;

}
}

}

/// @nodoc


class _WasteReductionSummary extends WasteReductionSummary {
  const _WasteReductionSummary({required this.period, required this.periodLabel, required this.itemsUsedBeforeExpiry, required this.wasteAvoidedKg, required this.dishesCooked, final  List<WasteReductionBar> weeklyBars = const <WasteReductionBar>[], final  List<WasteReductionCategory> byCategory = const <WasteReductionCategory>[]}): _weeklyBars = weeklyBars,_byCategory = byCategory,super._();
  

@override final  ReportPeriod period;
@override final  String periodLabel;
@override final  int itemsUsedBeforeExpiry;
@override final  double wasteAvoidedKg;
@override final  int dishesCooked;
 final  List<WasteReductionBar> _weeklyBars;
@override@JsonKey() List<WasteReductionBar> get weeklyBars {
  if (_weeklyBars is EqualUnmodifiableListView) return _weeklyBars;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_weeklyBars);
}

 final  List<WasteReductionCategory> _byCategory;
@override@JsonKey() List<WasteReductionCategory> get byCategory {
  if (_byCategory is EqualUnmodifiableListView) return _byCategory;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_byCategory);
}


/// Create a copy of WasteReductionSummary
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WasteReductionSummaryCopyWith<_WasteReductionSummary> get copyWith => __$WasteReductionSummaryCopyWithImpl<_WasteReductionSummary>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WasteReductionSummary&&(identical(other.period, period) || other.period == period)&&(identical(other.periodLabel, periodLabel) || other.periodLabel == periodLabel)&&(identical(other.itemsUsedBeforeExpiry, itemsUsedBeforeExpiry) || other.itemsUsedBeforeExpiry == itemsUsedBeforeExpiry)&&(identical(other.wasteAvoidedKg, wasteAvoidedKg) || other.wasteAvoidedKg == wasteAvoidedKg)&&(identical(other.dishesCooked, dishesCooked) || other.dishesCooked == dishesCooked)&&const DeepCollectionEquality().equals(other._weeklyBars, _weeklyBars)&&const DeepCollectionEquality().equals(other._byCategory, _byCategory));
}


@override
int get hashCode => Object.hash(runtimeType,period,periodLabel,itemsUsedBeforeExpiry,wasteAvoidedKg,dishesCooked,const DeepCollectionEquality().hash(_weeklyBars),const DeepCollectionEquality().hash(_byCategory));

@override
String toString() {
  return 'WasteReductionSummary(period: $period, periodLabel: $periodLabel, itemsUsedBeforeExpiry: $itemsUsedBeforeExpiry, wasteAvoidedKg: $wasteAvoidedKg, dishesCooked: $dishesCooked, weeklyBars: $weeklyBars, byCategory: $byCategory)';
}


}

/// @nodoc
abstract mixin class _$WasteReductionSummaryCopyWith<$Res> implements $WasteReductionSummaryCopyWith<$Res> {
  factory _$WasteReductionSummaryCopyWith(_WasteReductionSummary value, $Res Function(_WasteReductionSummary) _then) = __$WasteReductionSummaryCopyWithImpl;
@override @useResult
$Res call({
 ReportPeriod period, String periodLabel, int itemsUsedBeforeExpiry, double wasteAvoidedKg, int dishesCooked, List<WasteReductionBar> weeklyBars, List<WasteReductionCategory> byCategory
});




}
/// @nodoc
class __$WasteReductionSummaryCopyWithImpl<$Res>
    implements _$WasteReductionSummaryCopyWith<$Res> {
  __$WasteReductionSummaryCopyWithImpl(this._self, this._then);

  final _WasteReductionSummary _self;
  final $Res Function(_WasteReductionSummary) _then;

/// Create a copy of WasteReductionSummary
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? period = null,Object? periodLabel = null,Object? itemsUsedBeforeExpiry = null,Object? wasteAvoidedKg = null,Object? dishesCooked = null,Object? weeklyBars = null,Object? byCategory = null,}) {
  return _then(_WasteReductionSummary(
period: null == period ? _self.period : period // ignore: cast_nullable_to_non_nullable
as ReportPeriod,periodLabel: null == periodLabel ? _self.periodLabel : periodLabel // ignore: cast_nullable_to_non_nullable
as String,itemsUsedBeforeExpiry: null == itemsUsedBeforeExpiry ? _self.itemsUsedBeforeExpiry : itemsUsedBeforeExpiry // ignore: cast_nullable_to_non_nullable
as int,wasteAvoidedKg: null == wasteAvoidedKg ? _self.wasteAvoidedKg : wasteAvoidedKg // ignore: cast_nullable_to_non_nullable
as double,dishesCooked: null == dishesCooked ? _self.dishesCooked : dishesCooked // ignore: cast_nullable_to_non_nullable
as int,weeklyBars: null == weeklyBars ? _self._weeklyBars : weeklyBars // ignore: cast_nullable_to_non_nullable
as List<WasteReductionBar>,byCategory: null == byCategory ? _self._byCategory : byCategory // ignore: cast_nullable_to_non_nullable
as List<WasteReductionCategory>,
  ));
}


}

// dart format on
