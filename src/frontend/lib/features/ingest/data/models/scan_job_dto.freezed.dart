// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'scan_job_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ParsedItemDraftDto {

 String get name; String get category; double get quantity; String get unit;@JsonKey(name: 'storage_tier') String get storageTier;@JsonKey(name: 'packed_date') DateTime? get packedDate;@JsonKey(name: 'expiry_date') DateTime? get expiryDate;@JsonKey(name: 'price_vnd') int? get priceVnd;@JsonKey(name: 'is_expiry_warn') bool get isExpiryWarn;
/// Create a copy of ParsedItemDraftDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParsedItemDraftDtoCopyWith<ParsedItemDraftDto> get copyWith => _$ParsedItemDraftDtoCopyWithImpl<ParsedItemDraftDto>(this as ParsedItemDraftDto, _$identity);

  /// Serializes this ParsedItemDraftDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParsedItemDraftDto&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageTier, storageTier) || other.storageTier == storageTier)&&(identical(other.packedDate, packedDate) || other.packedDate == packedDate)&&(identical(other.expiryDate, expiryDate) || other.expiryDate == expiryDate)&&(identical(other.priceVnd, priceVnd) || other.priceVnd == priceVnd)&&(identical(other.isExpiryWarn, isExpiryWarn) || other.isExpiryWarn == isExpiryWarn));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,category,quantity,unit,storageTier,packedDate,expiryDate,priceVnd,isExpiryWarn);

@override
String toString() {
  return 'ParsedItemDraftDto(name: $name, category: $category, quantity: $quantity, unit: $unit, storageTier: $storageTier, packedDate: $packedDate, expiryDate: $expiryDate, priceVnd: $priceVnd, isExpiryWarn: $isExpiryWarn)';
}


}

/// @nodoc
abstract mixin class $ParsedItemDraftDtoCopyWith<$Res>  {
  factory $ParsedItemDraftDtoCopyWith(ParsedItemDraftDto value, $Res Function(ParsedItemDraftDto) _then) = _$ParsedItemDraftDtoCopyWithImpl;
@useResult
$Res call({
 String name, String category, double quantity, String unit,@JsonKey(name: 'storage_tier') String storageTier,@JsonKey(name: 'packed_date') DateTime? packedDate,@JsonKey(name: 'expiry_date') DateTime? expiryDate,@JsonKey(name: 'price_vnd') int? priceVnd,@JsonKey(name: 'is_expiry_warn') bool isExpiryWarn
});




}
/// @nodoc
class _$ParsedItemDraftDtoCopyWithImpl<$Res>
    implements $ParsedItemDraftDtoCopyWith<$Res> {
  _$ParsedItemDraftDtoCopyWithImpl(this._self, this._then);

  final ParsedItemDraftDto _self;
  final $Res Function(ParsedItemDraftDto) _then;

/// Create a copy of ParsedItemDraftDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? category = null,Object? quantity = null,Object? unit = null,Object? storageTier = null,Object? packedDate = freezed,Object? expiryDate = freezed,Object? priceVnd = freezed,Object? isExpiryWarn = null,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,storageTier: null == storageTier ? _self.storageTier : storageTier // ignore: cast_nullable_to_non_nullable
as String,packedDate: freezed == packedDate ? _self.packedDate : packedDate // ignore: cast_nullable_to_non_nullable
as DateTime?,expiryDate: freezed == expiryDate ? _self.expiryDate : expiryDate // ignore: cast_nullable_to_non_nullable
as DateTime?,priceVnd: freezed == priceVnd ? _self.priceVnd : priceVnd // ignore: cast_nullable_to_non_nullable
as int?,isExpiryWarn: null == isExpiryWarn ? _self.isExpiryWarn : isExpiryWarn // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [ParsedItemDraftDto].
extension ParsedItemDraftDtoPatterns on ParsedItemDraftDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ParsedItemDraftDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ParsedItemDraftDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ParsedItemDraftDto value)  $default,){
final _that = this;
switch (_that) {
case _ParsedItemDraftDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ParsedItemDraftDto value)?  $default,){
final _that = this;
switch (_that) {
case _ParsedItemDraftDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String name,  String category,  double quantity,  String unit, @JsonKey(name: 'storage_tier')  String storageTier, @JsonKey(name: 'packed_date')  DateTime? packedDate, @JsonKey(name: 'expiry_date')  DateTime? expiryDate, @JsonKey(name: 'price_vnd')  int? priceVnd, @JsonKey(name: 'is_expiry_warn')  bool isExpiryWarn)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ParsedItemDraftDto() when $default != null:
return $default(_that.name,_that.category,_that.quantity,_that.unit,_that.storageTier,_that.packedDate,_that.expiryDate,_that.priceVnd,_that.isExpiryWarn);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String name,  String category,  double quantity,  String unit, @JsonKey(name: 'storage_tier')  String storageTier, @JsonKey(name: 'packed_date')  DateTime? packedDate, @JsonKey(name: 'expiry_date')  DateTime? expiryDate, @JsonKey(name: 'price_vnd')  int? priceVnd, @JsonKey(name: 'is_expiry_warn')  bool isExpiryWarn)  $default,) {final _that = this;
switch (_that) {
case _ParsedItemDraftDto():
return $default(_that.name,_that.category,_that.quantity,_that.unit,_that.storageTier,_that.packedDate,_that.expiryDate,_that.priceVnd,_that.isExpiryWarn);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String name,  String category,  double quantity,  String unit, @JsonKey(name: 'storage_tier')  String storageTier, @JsonKey(name: 'packed_date')  DateTime? packedDate, @JsonKey(name: 'expiry_date')  DateTime? expiryDate, @JsonKey(name: 'price_vnd')  int? priceVnd, @JsonKey(name: 'is_expiry_warn')  bool isExpiryWarn)?  $default,) {final _that = this;
switch (_that) {
case _ParsedItemDraftDto() when $default != null:
return $default(_that.name,_that.category,_that.quantity,_that.unit,_that.storageTier,_that.packedDate,_that.expiryDate,_that.priceVnd,_that.isExpiryWarn);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ParsedItemDraftDto extends ParsedItemDraftDto {
  const _ParsedItemDraftDto({this.name = '', this.category = '', this.quantity = 0, this.unit = 'g', @JsonKey(name: 'storage_tier') this.storageTier = 'fridge', @JsonKey(name: 'packed_date') this.packedDate, @JsonKey(name: 'expiry_date') this.expiryDate, @JsonKey(name: 'price_vnd') this.priceVnd, @JsonKey(name: 'is_expiry_warn') this.isExpiryWarn = false}): super._();
  factory _ParsedItemDraftDto.fromJson(Map<String, dynamic> json) => _$ParsedItemDraftDtoFromJson(json);

@override@JsonKey() final  String name;
@override@JsonKey() final  String category;
@override@JsonKey() final  double quantity;
@override@JsonKey() final  String unit;
@override@JsonKey(name: 'storage_tier') final  String storageTier;
@override@JsonKey(name: 'packed_date') final  DateTime? packedDate;
@override@JsonKey(name: 'expiry_date') final  DateTime? expiryDate;
@override@JsonKey(name: 'price_vnd') final  int? priceVnd;
@override@JsonKey(name: 'is_expiry_warn') final  bool isExpiryWarn;

/// Create a copy of ParsedItemDraftDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ParsedItemDraftDtoCopyWith<_ParsedItemDraftDto> get copyWith => __$ParsedItemDraftDtoCopyWithImpl<_ParsedItemDraftDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ParsedItemDraftDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ParsedItemDraftDto&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageTier, storageTier) || other.storageTier == storageTier)&&(identical(other.packedDate, packedDate) || other.packedDate == packedDate)&&(identical(other.expiryDate, expiryDate) || other.expiryDate == expiryDate)&&(identical(other.priceVnd, priceVnd) || other.priceVnd == priceVnd)&&(identical(other.isExpiryWarn, isExpiryWarn) || other.isExpiryWarn == isExpiryWarn));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,category,quantity,unit,storageTier,packedDate,expiryDate,priceVnd,isExpiryWarn);

@override
String toString() {
  return 'ParsedItemDraftDto(name: $name, category: $category, quantity: $quantity, unit: $unit, storageTier: $storageTier, packedDate: $packedDate, expiryDate: $expiryDate, priceVnd: $priceVnd, isExpiryWarn: $isExpiryWarn)';
}


}

/// @nodoc
abstract mixin class _$ParsedItemDraftDtoCopyWith<$Res> implements $ParsedItemDraftDtoCopyWith<$Res> {
  factory _$ParsedItemDraftDtoCopyWith(_ParsedItemDraftDto value, $Res Function(_ParsedItemDraftDto) _then) = __$ParsedItemDraftDtoCopyWithImpl;
@override @useResult
$Res call({
 String name, String category, double quantity, String unit,@JsonKey(name: 'storage_tier') String storageTier,@JsonKey(name: 'packed_date') DateTime? packedDate,@JsonKey(name: 'expiry_date') DateTime? expiryDate,@JsonKey(name: 'price_vnd') int? priceVnd,@JsonKey(name: 'is_expiry_warn') bool isExpiryWarn
});




}
/// @nodoc
class __$ParsedItemDraftDtoCopyWithImpl<$Res>
    implements _$ParsedItemDraftDtoCopyWith<$Res> {
  __$ParsedItemDraftDtoCopyWithImpl(this._self, this._then);

  final _ParsedItemDraftDto _self;
  final $Res Function(_ParsedItemDraftDto) _then;

/// Create a copy of ParsedItemDraftDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? category = null,Object? quantity = null,Object? unit = null,Object? storageTier = null,Object? packedDate = freezed,Object? expiryDate = freezed,Object? priceVnd = freezed,Object? isExpiryWarn = null,}) {
  return _then(_ParsedItemDraftDto(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,storageTier: null == storageTier ? _self.storageTier : storageTier // ignore: cast_nullable_to_non_nullable
as String,packedDate: freezed == packedDate ? _self.packedDate : packedDate // ignore: cast_nullable_to_non_nullable
as DateTime?,expiryDate: freezed == expiryDate ? _self.expiryDate : expiryDate // ignore: cast_nullable_to_non_nullable
as DateTime?,priceVnd: freezed == priceVnd ? _self.priceVnd : priceVnd // ignore: cast_nullable_to_non_nullable
as int?,isExpiryWarn: null == isExpiryWarn ? _self.isExpiryWarn : isExpiryWarn // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$ScanJobDto {

@JsonKey(name: 'job_id') String get jobId; String get type; String get status;@JsonKey(name: 'raw_text') String? get rawText;@JsonKey(name: 'raw_transcript') String? get rawTranscript;@JsonKey(name: 'store_name') String? get storeName;@JsonKey(name: 'purchase_date') DateTime? get purchaseDate;@JsonKey(name: 'field_count') int? get fieldCount;/// Label jobs return a single [item]; receipt / voice return [items].
 ParsedItemDraftDto? get item; List<ParsedItemDraftDto> get items;
/// Create a copy of ScanJobDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ScanJobDtoCopyWith<ScanJobDto> get copyWith => _$ScanJobDtoCopyWithImpl<ScanJobDto>(this as ScanJobDto, _$identity);

  /// Serializes this ScanJobDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ScanJobDto&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.type, type) || other.type == type)&&(identical(other.status, status) || other.status == status)&&(identical(other.rawText, rawText) || other.rawText == rawText)&&(identical(other.rawTranscript, rawTranscript) || other.rawTranscript == rawTranscript)&&(identical(other.storeName, storeName) || other.storeName == storeName)&&(identical(other.purchaseDate, purchaseDate) || other.purchaseDate == purchaseDate)&&(identical(other.fieldCount, fieldCount) || other.fieldCount == fieldCount)&&(identical(other.item, item) || other.item == item)&&const DeepCollectionEquality().equals(other.items, items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,jobId,type,status,rawText,rawTranscript,storeName,purchaseDate,fieldCount,item,const DeepCollectionEquality().hash(items));

@override
String toString() {
  return 'ScanJobDto(jobId: $jobId, type: $type, status: $status, rawText: $rawText, rawTranscript: $rawTranscript, storeName: $storeName, purchaseDate: $purchaseDate, fieldCount: $fieldCount, item: $item, items: $items)';
}


}

/// @nodoc
abstract mixin class $ScanJobDtoCopyWith<$Res>  {
  factory $ScanJobDtoCopyWith(ScanJobDto value, $Res Function(ScanJobDto) _then) = _$ScanJobDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'job_id') String jobId, String type, String status,@JsonKey(name: 'raw_text') String? rawText,@JsonKey(name: 'raw_transcript') String? rawTranscript,@JsonKey(name: 'store_name') String? storeName,@JsonKey(name: 'purchase_date') DateTime? purchaseDate,@JsonKey(name: 'field_count') int? fieldCount, ParsedItemDraftDto? item, List<ParsedItemDraftDto> items
});


$ParsedItemDraftDtoCopyWith<$Res>? get item;

}
/// @nodoc
class _$ScanJobDtoCopyWithImpl<$Res>
    implements $ScanJobDtoCopyWith<$Res> {
  _$ScanJobDtoCopyWithImpl(this._self, this._then);

  final ScanJobDto _self;
  final $Res Function(ScanJobDto) _then;

/// Create a copy of ScanJobDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? jobId = null,Object? type = null,Object? status = null,Object? rawText = freezed,Object? rawTranscript = freezed,Object? storeName = freezed,Object? purchaseDate = freezed,Object? fieldCount = freezed,Object? item = freezed,Object? items = null,}) {
  return _then(_self.copyWith(
jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,rawText: freezed == rawText ? _self.rawText : rawText // ignore: cast_nullable_to_non_nullable
as String?,rawTranscript: freezed == rawTranscript ? _self.rawTranscript : rawTranscript // ignore: cast_nullable_to_non_nullable
as String?,storeName: freezed == storeName ? _self.storeName : storeName // ignore: cast_nullable_to_non_nullable
as String?,purchaseDate: freezed == purchaseDate ? _self.purchaseDate : purchaseDate // ignore: cast_nullable_to_non_nullable
as DateTime?,fieldCount: freezed == fieldCount ? _self.fieldCount : fieldCount // ignore: cast_nullable_to_non_nullable
as int?,item: freezed == item ? _self.item : item // ignore: cast_nullable_to_non_nullable
as ParsedItemDraftDto?,items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<ParsedItemDraftDto>,
  ));
}
/// Create a copy of ScanJobDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParsedItemDraftDtoCopyWith<$Res>? get item {
    if (_self.item == null) {
    return null;
  }

  return $ParsedItemDraftDtoCopyWith<$Res>(_self.item!, (value) {
    return _then(_self.copyWith(item: value));
  });
}
}


/// Adds pattern-matching-related methods to [ScanJobDto].
extension ScanJobDtoPatterns on ScanJobDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ScanJobDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ScanJobDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ScanJobDto value)  $default,){
final _that = this;
switch (_that) {
case _ScanJobDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ScanJobDto value)?  $default,){
final _that = this;
switch (_that) {
case _ScanJobDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'job_id')  String jobId,  String type,  String status, @JsonKey(name: 'raw_text')  String? rawText, @JsonKey(name: 'raw_transcript')  String? rawTranscript, @JsonKey(name: 'store_name')  String? storeName, @JsonKey(name: 'purchase_date')  DateTime? purchaseDate, @JsonKey(name: 'field_count')  int? fieldCount,  ParsedItemDraftDto? item,  List<ParsedItemDraftDto> items)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ScanJobDto() when $default != null:
return $default(_that.jobId,_that.type,_that.status,_that.rawText,_that.rawTranscript,_that.storeName,_that.purchaseDate,_that.fieldCount,_that.item,_that.items);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'job_id')  String jobId,  String type,  String status, @JsonKey(name: 'raw_text')  String? rawText, @JsonKey(name: 'raw_transcript')  String? rawTranscript, @JsonKey(name: 'store_name')  String? storeName, @JsonKey(name: 'purchase_date')  DateTime? purchaseDate, @JsonKey(name: 'field_count')  int? fieldCount,  ParsedItemDraftDto? item,  List<ParsedItemDraftDto> items)  $default,) {final _that = this;
switch (_that) {
case _ScanJobDto():
return $default(_that.jobId,_that.type,_that.status,_that.rawText,_that.rawTranscript,_that.storeName,_that.purchaseDate,_that.fieldCount,_that.item,_that.items);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'job_id')  String jobId,  String type,  String status, @JsonKey(name: 'raw_text')  String? rawText, @JsonKey(name: 'raw_transcript')  String? rawTranscript, @JsonKey(name: 'store_name')  String? storeName, @JsonKey(name: 'purchase_date')  DateTime? purchaseDate, @JsonKey(name: 'field_count')  int? fieldCount,  ParsedItemDraftDto? item,  List<ParsedItemDraftDto> items)?  $default,) {final _that = this;
switch (_that) {
case _ScanJobDto() when $default != null:
return $default(_that.jobId,_that.type,_that.status,_that.rawText,_that.rawTranscript,_that.storeName,_that.purchaseDate,_that.fieldCount,_that.item,_that.items);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ScanJobDto extends ScanJobDto {
  const _ScanJobDto({@JsonKey(name: 'job_id') required this.jobId, required this.type, this.status = 'completed', @JsonKey(name: 'raw_text') this.rawText, @JsonKey(name: 'raw_transcript') this.rawTranscript, @JsonKey(name: 'store_name') this.storeName, @JsonKey(name: 'purchase_date') this.purchaseDate, @JsonKey(name: 'field_count') this.fieldCount, this.item, final  List<ParsedItemDraftDto> items = const <ParsedItemDraftDto>[]}): _items = items,super._();
  factory _ScanJobDto.fromJson(Map<String, dynamic> json) => _$ScanJobDtoFromJson(json);

@override@JsonKey(name: 'job_id') final  String jobId;
@override final  String type;
@override@JsonKey() final  String status;
@override@JsonKey(name: 'raw_text') final  String? rawText;
@override@JsonKey(name: 'raw_transcript') final  String? rawTranscript;
@override@JsonKey(name: 'store_name') final  String? storeName;
@override@JsonKey(name: 'purchase_date') final  DateTime? purchaseDate;
@override@JsonKey(name: 'field_count') final  int? fieldCount;
/// Label jobs return a single [item]; receipt / voice return [items].
@override final  ParsedItemDraftDto? item;
 final  List<ParsedItemDraftDto> _items;
@override@JsonKey() List<ParsedItemDraftDto> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


/// Create a copy of ScanJobDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ScanJobDtoCopyWith<_ScanJobDto> get copyWith => __$ScanJobDtoCopyWithImpl<_ScanJobDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ScanJobDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ScanJobDto&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.type, type) || other.type == type)&&(identical(other.status, status) || other.status == status)&&(identical(other.rawText, rawText) || other.rawText == rawText)&&(identical(other.rawTranscript, rawTranscript) || other.rawTranscript == rawTranscript)&&(identical(other.storeName, storeName) || other.storeName == storeName)&&(identical(other.purchaseDate, purchaseDate) || other.purchaseDate == purchaseDate)&&(identical(other.fieldCount, fieldCount) || other.fieldCount == fieldCount)&&(identical(other.item, item) || other.item == item)&&const DeepCollectionEquality().equals(other._items, _items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,jobId,type,status,rawText,rawTranscript,storeName,purchaseDate,fieldCount,item,const DeepCollectionEquality().hash(_items));

@override
String toString() {
  return 'ScanJobDto(jobId: $jobId, type: $type, status: $status, rawText: $rawText, rawTranscript: $rawTranscript, storeName: $storeName, purchaseDate: $purchaseDate, fieldCount: $fieldCount, item: $item, items: $items)';
}


}

/// @nodoc
abstract mixin class _$ScanJobDtoCopyWith<$Res> implements $ScanJobDtoCopyWith<$Res> {
  factory _$ScanJobDtoCopyWith(_ScanJobDto value, $Res Function(_ScanJobDto) _then) = __$ScanJobDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'job_id') String jobId, String type, String status,@JsonKey(name: 'raw_text') String? rawText,@JsonKey(name: 'raw_transcript') String? rawTranscript,@JsonKey(name: 'store_name') String? storeName,@JsonKey(name: 'purchase_date') DateTime? purchaseDate,@JsonKey(name: 'field_count') int? fieldCount, ParsedItemDraftDto? item, List<ParsedItemDraftDto> items
});


@override $ParsedItemDraftDtoCopyWith<$Res>? get item;

}
/// @nodoc
class __$ScanJobDtoCopyWithImpl<$Res>
    implements _$ScanJobDtoCopyWith<$Res> {
  __$ScanJobDtoCopyWithImpl(this._self, this._then);

  final _ScanJobDto _self;
  final $Res Function(_ScanJobDto) _then;

/// Create a copy of ScanJobDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? jobId = null,Object? type = null,Object? status = null,Object? rawText = freezed,Object? rawTranscript = freezed,Object? storeName = freezed,Object? purchaseDate = freezed,Object? fieldCount = freezed,Object? item = freezed,Object? items = null,}) {
  return _then(_ScanJobDto(
jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,rawText: freezed == rawText ? _self.rawText : rawText // ignore: cast_nullable_to_non_nullable
as String?,rawTranscript: freezed == rawTranscript ? _self.rawTranscript : rawTranscript // ignore: cast_nullable_to_non_nullable
as String?,storeName: freezed == storeName ? _self.storeName : storeName // ignore: cast_nullable_to_non_nullable
as String?,purchaseDate: freezed == purchaseDate ? _self.purchaseDate : purchaseDate // ignore: cast_nullable_to_non_nullable
as DateTime?,fieldCount: freezed == fieldCount ? _self.fieldCount : fieldCount // ignore: cast_nullable_to_non_nullable
as int?,item: freezed == item ? _self.item : item // ignore: cast_nullable_to_non_nullable
as ParsedItemDraftDto?,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<ParsedItemDraftDto>,
  ));
}

/// Create a copy of ScanJobDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParsedItemDraftDtoCopyWith<$Res>? get item {
    if (_self.item == null) {
    return null;
  }

  return $ParsedItemDraftDtoCopyWith<$Res>(_self.item!, (value) {
    return _then(_self.copyWith(item: value));
  });
}
}

// dart format on
