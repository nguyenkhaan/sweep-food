// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'scan_job.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ScanJob {

 String get id; ScanType get type; ScanStatus get status;/// Extracted drafts. Label jobs carry exactly one; receipt / voice carry many.
 List<ParsedItemDraft> get items;/// OCR raw text (label / receipt) or ASR transcript (voice), for display.
 String? get rawText;/// Receipt only.
 String? get storeName; DateTime? get purchaseDate;/// How many label fields the OCR filled (I-03 banner).
 int? get fieldCount;/// Local path of the captured photo / audio, kept for the review thumbnail.
/// Filled client-side by the repository, never by the server.
 String? get sourcePath;
/// Create a copy of ScanJob
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ScanJobCopyWith<ScanJob> get copyWith => _$ScanJobCopyWithImpl<ScanJob>(this as ScanJob, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ScanJob&&(identical(other.id, id) || other.id == id)&&(identical(other.type, type) || other.type == type)&&(identical(other.status, status) || other.status == status)&&const DeepCollectionEquality().equals(other.items, items)&&(identical(other.rawText, rawText) || other.rawText == rawText)&&(identical(other.storeName, storeName) || other.storeName == storeName)&&(identical(other.purchaseDate, purchaseDate) || other.purchaseDate == purchaseDate)&&(identical(other.fieldCount, fieldCount) || other.fieldCount == fieldCount)&&(identical(other.sourcePath, sourcePath) || other.sourcePath == sourcePath));
}


@override
int get hashCode => Object.hash(runtimeType,id,type,status,const DeepCollectionEquality().hash(items),rawText,storeName,purchaseDate,fieldCount,sourcePath);

@override
String toString() {
  return 'ScanJob(id: $id, type: $type, status: $status, items: $items, rawText: $rawText, storeName: $storeName, purchaseDate: $purchaseDate, fieldCount: $fieldCount, sourcePath: $sourcePath)';
}


}

/// @nodoc
abstract mixin class $ScanJobCopyWith<$Res>  {
  factory $ScanJobCopyWith(ScanJob value, $Res Function(ScanJob) _then) = _$ScanJobCopyWithImpl;
@useResult
$Res call({
 String id, ScanType type, ScanStatus status, List<ParsedItemDraft> items, String? rawText, String? storeName, DateTime? purchaseDate, int? fieldCount, String? sourcePath
});




}
/// @nodoc
class _$ScanJobCopyWithImpl<$Res>
    implements $ScanJobCopyWith<$Res> {
  _$ScanJobCopyWithImpl(this._self, this._then);

  final ScanJob _self;
  final $Res Function(ScanJob) _then;

/// Create a copy of ScanJob
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? type = null,Object? status = null,Object? items = null,Object? rawText = freezed,Object? storeName = freezed,Object? purchaseDate = freezed,Object? fieldCount = freezed,Object? sourcePath = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as ScanType,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ScanStatus,items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<ParsedItemDraft>,rawText: freezed == rawText ? _self.rawText : rawText // ignore: cast_nullable_to_non_nullable
as String?,storeName: freezed == storeName ? _self.storeName : storeName // ignore: cast_nullable_to_non_nullable
as String?,purchaseDate: freezed == purchaseDate ? _self.purchaseDate : purchaseDate // ignore: cast_nullable_to_non_nullable
as DateTime?,fieldCount: freezed == fieldCount ? _self.fieldCount : fieldCount // ignore: cast_nullable_to_non_nullable
as int?,sourcePath: freezed == sourcePath ? _self.sourcePath : sourcePath // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ScanJob].
extension ScanJobPatterns on ScanJob {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ScanJob value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ScanJob() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ScanJob value)  $default,){
final _that = this;
switch (_that) {
case _ScanJob():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ScanJob value)?  $default,){
final _that = this;
switch (_that) {
case _ScanJob() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  ScanType type,  ScanStatus status,  List<ParsedItemDraft> items,  String? rawText,  String? storeName,  DateTime? purchaseDate,  int? fieldCount,  String? sourcePath)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ScanJob() when $default != null:
return $default(_that.id,_that.type,_that.status,_that.items,_that.rawText,_that.storeName,_that.purchaseDate,_that.fieldCount,_that.sourcePath);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  ScanType type,  ScanStatus status,  List<ParsedItemDraft> items,  String? rawText,  String? storeName,  DateTime? purchaseDate,  int? fieldCount,  String? sourcePath)  $default,) {final _that = this;
switch (_that) {
case _ScanJob():
return $default(_that.id,_that.type,_that.status,_that.items,_that.rawText,_that.storeName,_that.purchaseDate,_that.fieldCount,_that.sourcePath);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  ScanType type,  ScanStatus status,  List<ParsedItemDraft> items,  String? rawText,  String? storeName,  DateTime? purchaseDate,  int? fieldCount,  String? sourcePath)?  $default,) {final _that = this;
switch (_that) {
case _ScanJob() when $default != null:
return $default(_that.id,_that.type,_that.status,_that.items,_that.rawText,_that.storeName,_that.purchaseDate,_that.fieldCount,_that.sourcePath);case _:
  return null;

}
}

}

/// @nodoc


class _ScanJob extends ScanJob {
  const _ScanJob({required this.id, required this.type, this.status = ScanStatus.completed, final  List<ParsedItemDraft> items = const <ParsedItemDraft>[], this.rawText, this.storeName, this.purchaseDate, this.fieldCount, this.sourcePath}): _items = items,super._();
  

@override final  String id;
@override final  ScanType type;
@override@JsonKey() final  ScanStatus status;
/// Extracted drafts. Label jobs carry exactly one; receipt / voice carry many.
 final  List<ParsedItemDraft> _items;
/// Extracted drafts. Label jobs carry exactly one; receipt / voice carry many.
@override@JsonKey() List<ParsedItemDraft> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}

/// OCR raw text (label / receipt) or ASR transcript (voice), for display.
@override final  String? rawText;
/// Receipt only.
@override final  String? storeName;
@override final  DateTime? purchaseDate;
/// How many label fields the OCR filled (I-03 banner).
@override final  int? fieldCount;
/// Local path of the captured photo / audio, kept for the review thumbnail.
/// Filled client-side by the repository, never by the server.
@override final  String? sourcePath;

/// Create a copy of ScanJob
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ScanJobCopyWith<_ScanJob> get copyWith => __$ScanJobCopyWithImpl<_ScanJob>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ScanJob&&(identical(other.id, id) || other.id == id)&&(identical(other.type, type) || other.type == type)&&(identical(other.status, status) || other.status == status)&&const DeepCollectionEquality().equals(other._items, _items)&&(identical(other.rawText, rawText) || other.rawText == rawText)&&(identical(other.storeName, storeName) || other.storeName == storeName)&&(identical(other.purchaseDate, purchaseDate) || other.purchaseDate == purchaseDate)&&(identical(other.fieldCount, fieldCount) || other.fieldCount == fieldCount)&&(identical(other.sourcePath, sourcePath) || other.sourcePath == sourcePath));
}


@override
int get hashCode => Object.hash(runtimeType,id,type,status,const DeepCollectionEquality().hash(_items),rawText,storeName,purchaseDate,fieldCount,sourcePath);

@override
String toString() {
  return 'ScanJob(id: $id, type: $type, status: $status, items: $items, rawText: $rawText, storeName: $storeName, purchaseDate: $purchaseDate, fieldCount: $fieldCount, sourcePath: $sourcePath)';
}


}

/// @nodoc
abstract mixin class _$ScanJobCopyWith<$Res> implements $ScanJobCopyWith<$Res> {
  factory _$ScanJobCopyWith(_ScanJob value, $Res Function(_ScanJob) _then) = __$ScanJobCopyWithImpl;
@override @useResult
$Res call({
 String id, ScanType type, ScanStatus status, List<ParsedItemDraft> items, String? rawText, String? storeName, DateTime? purchaseDate, int? fieldCount, String? sourcePath
});




}
/// @nodoc
class __$ScanJobCopyWithImpl<$Res>
    implements _$ScanJobCopyWith<$Res> {
  __$ScanJobCopyWithImpl(this._self, this._then);

  final _ScanJob _self;
  final $Res Function(_ScanJob) _then;

/// Create a copy of ScanJob
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? type = null,Object? status = null,Object? items = null,Object? rawText = freezed,Object? storeName = freezed,Object? purchaseDate = freezed,Object? fieldCount = freezed,Object? sourcePath = freezed,}) {
  return _then(_ScanJob(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as ScanType,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ScanStatus,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<ParsedItemDraft>,rawText: freezed == rawText ? _self.rawText : rawText // ignore: cast_nullable_to_non_nullable
as String?,storeName: freezed == storeName ? _self.storeName : storeName // ignore: cast_nullable_to_non_nullable
as String?,purchaseDate: freezed == purchaseDate ? _self.purchaseDate : purchaseDate // ignore: cast_nullable_to_non_nullable
as DateTime?,fieldCount: freezed == fieldCount ? _self.fieldCount : fieldCount // ignore: cast_nullable_to_non_nullable
as int?,sourcePath: freezed == sourcePath ? _self.sourcePath : sourcePath // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
