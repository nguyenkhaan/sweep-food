// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'pantry_item_draft.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$PantryItemDraft {
  String get name;
  String get category;
  double get quantity;
  MeasurementUnit get unit;
  StorageTier get storageTier;
  PantrySource get source;
  String? get ingredientId;
  DateTime? get packedDate;
  DateTime? get expiryDate;
  int? get referenceShelfLifeDays;
  int? get priceVnd;

  /// Create a copy of PantryItemDraft
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $PantryItemDraftCopyWith<PantryItemDraft> get copyWith =>
      _$PantryItemDraftCopyWithImpl<PantryItemDraft>(
          this as PantryItemDraft, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is PantryItemDraft &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.quantity, quantity) ||
                other.quantity == quantity) &&
            (identical(other.unit, unit) || other.unit == unit) &&
            (identical(other.storageTier, storageTier) ||
                other.storageTier == storageTier) &&
            (identical(other.source, source) || other.source == source) &&
            (identical(other.ingredientId, ingredientId) ||
                other.ingredientId == ingredientId) &&
            (identical(other.packedDate, packedDate) ||
                other.packedDate == packedDate) &&
            (identical(other.expiryDate, expiryDate) ||
                other.expiryDate == expiryDate) &&
            (identical(other.referenceShelfLifeDays, referenceShelfLifeDays) ||
                other.referenceShelfLifeDays == referenceShelfLifeDays) &&
            (identical(other.priceVnd, priceVnd) ||
                other.priceVnd == priceVnd));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      name,
      category,
      quantity,
      unit,
      storageTier,
      source,
      ingredientId,
      packedDate,
      expiryDate,
      referenceShelfLifeDays,
      priceVnd);

  @override
  String toString() {
    return 'PantryItemDraft(name: $name, category: $category, quantity: $quantity, unit: $unit, storageTier: $storageTier, source: $source, ingredientId: $ingredientId, packedDate: $packedDate, expiryDate: $expiryDate, referenceShelfLifeDays: $referenceShelfLifeDays, priceVnd: $priceVnd)';
  }
}

/// @nodoc
abstract mixin class $PantryItemDraftCopyWith<$Res> {
  factory $PantryItemDraftCopyWith(
          PantryItemDraft value, $Res Function(PantryItemDraft) _then) =
      _$PantryItemDraftCopyWithImpl;
  @useResult
  $Res call(
      {String name,
      String category,
      double quantity,
      MeasurementUnit unit,
      StorageTier storageTier,
      PantrySource source,
      String? ingredientId,
      DateTime? packedDate,
      DateTime? expiryDate,
      int? referenceShelfLifeDays,
      int? priceVnd});
}

/// @nodoc
class _$PantryItemDraftCopyWithImpl<$Res>
    implements $PantryItemDraftCopyWith<$Res> {
  _$PantryItemDraftCopyWithImpl(this._self, this._then);

  final PantryItemDraft _self;
  final $Res Function(PantryItemDraft) _then;

  /// Create a copy of PantryItemDraft
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? category = null,
    Object? quantity = null,
    Object? unit = null,
    Object? storageTier = null,
    Object? source = null,
    Object? ingredientId = freezed,
    Object? packedDate = freezed,
    Object? expiryDate = freezed,
    Object? referenceShelfLifeDays = freezed,
    Object? priceVnd = freezed,
  }) {
    return _then(_self.copyWith(
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      category: null == category
          ? _self.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      quantity: null == quantity
          ? _self.quantity
          : quantity // ignore: cast_nullable_to_non_nullable
              as double,
      unit: null == unit
          ? _self.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as MeasurementUnit,
      storageTier: null == storageTier
          ? _self.storageTier
          : storageTier // ignore: cast_nullable_to_non_nullable
              as StorageTier,
      source: null == source
          ? _self.source
          : source // ignore: cast_nullable_to_non_nullable
              as PantrySource,
      ingredientId: freezed == ingredientId
          ? _self.ingredientId
          : ingredientId // ignore: cast_nullable_to_non_nullable
              as String?,
      packedDate: freezed == packedDate
          ? _self.packedDate
          : packedDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      expiryDate: freezed == expiryDate
          ? _self.expiryDate
          : expiryDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      referenceShelfLifeDays: freezed == referenceShelfLifeDays
          ? _self.referenceShelfLifeDays
          : referenceShelfLifeDays // ignore: cast_nullable_to_non_nullable
              as int?,
      priceVnd: freezed == priceVnd
          ? _self.priceVnd
          : priceVnd // ignore: cast_nullable_to_non_nullable
              as int?,
    ));
  }
}

/// Adds pattern-matching-related methods to [PantryItemDraft].
extension PantryItemDraftPatterns on PantryItemDraft {
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

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>(
    TResult Function(_PantryItemDraft value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _PantryItemDraft() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult map<TResult extends Object?>(
    TResult Function(_PantryItemDraft value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _PantryItemDraft():
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>(
    TResult? Function(_PantryItemDraft value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _PantryItemDraft() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>(
    TResult Function(
            String name,
            String category,
            double quantity,
            MeasurementUnit unit,
            StorageTier storageTier,
            PantrySource source,
            String? ingredientId,
            DateTime? packedDate,
            DateTime? expiryDate,
            int? referenceShelfLifeDays,
            int? priceVnd)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _PantryItemDraft() when $default != null:
        return $default(
            _that.name,
            _that.category,
            _that.quantity,
            _that.unit,
            _that.storageTier,
            _that.source,
            _that.ingredientId,
            _that.packedDate,
            _that.expiryDate,
            _that.referenceShelfLifeDays,
            _that.priceVnd);
      case _:
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

  @optionalTypeArgs
  TResult when<TResult extends Object?>(
    TResult Function(
            String name,
            String category,
            double quantity,
            MeasurementUnit unit,
            StorageTier storageTier,
            PantrySource source,
            String? ingredientId,
            DateTime? packedDate,
            DateTime? expiryDate,
            int? referenceShelfLifeDays,
            int? priceVnd)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _PantryItemDraft():
        return $default(
            _that.name,
            _that.category,
            _that.quantity,
            _that.unit,
            _that.storageTier,
            _that.source,
            _that.ingredientId,
            _that.packedDate,
            _that.expiryDate,
            _that.referenceShelfLifeDays,
            _that.priceVnd);
      case _:
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

  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>(
    TResult? Function(
            String name,
            String category,
            double quantity,
            MeasurementUnit unit,
            StorageTier storageTier,
            PantrySource source,
            String? ingredientId,
            DateTime? packedDate,
            DateTime? expiryDate,
            int? referenceShelfLifeDays,
            int? priceVnd)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _PantryItemDraft() when $default != null:
        return $default(
            _that.name,
            _that.category,
            _that.quantity,
            _that.unit,
            _that.storageTier,
            _that.source,
            _that.ingredientId,
            _that.packedDate,
            _that.expiryDate,
            _that.referenceShelfLifeDays,
            _that.priceVnd);
      case _:
        return null;
    }
  }
}

/// @nodoc

class _PantryItemDraft extends PantryItemDraft {
  const _PantryItemDraft(
      {this.name = '',
      this.category = '',
      this.quantity = 0,
      this.unit = MeasurementUnit.gram,
      this.storageTier = StorageTier.fridge,
      this.source = PantrySource.manual,
      this.ingredientId,
      this.packedDate,
      this.expiryDate,
      this.referenceShelfLifeDays,
      this.priceVnd})
      : super._();

  @override
  @JsonKey()
  final String name;
  @override
  @JsonKey()
  final String category;
  @override
  @JsonKey()
  final double quantity;
  @override
  @JsonKey()
  final MeasurementUnit unit;
  @override
  @JsonKey()
  final StorageTier storageTier;
  @override
  @JsonKey()
  final PantrySource source;
  @override
  final String? ingredientId;
  @override
  final DateTime? packedDate;
  @override
  final DateTime? expiryDate;
  @override
  final int? referenceShelfLifeDays;
  @override
  final int? priceVnd;

  /// Create a copy of PantryItemDraft
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$PantryItemDraftCopyWith<_PantryItemDraft> get copyWith =>
      __$PantryItemDraftCopyWithImpl<_PantryItemDraft>(this, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _PantryItemDraft &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.quantity, quantity) ||
                other.quantity == quantity) &&
            (identical(other.unit, unit) || other.unit == unit) &&
            (identical(other.storageTier, storageTier) ||
                other.storageTier == storageTier) &&
            (identical(other.source, source) || other.source == source) &&
            (identical(other.ingredientId, ingredientId) ||
                other.ingredientId == ingredientId) &&
            (identical(other.packedDate, packedDate) ||
                other.packedDate == packedDate) &&
            (identical(other.expiryDate, expiryDate) ||
                other.expiryDate == expiryDate) &&
            (identical(other.referenceShelfLifeDays, referenceShelfLifeDays) ||
                other.referenceShelfLifeDays == referenceShelfLifeDays) &&
            (identical(other.priceVnd, priceVnd) ||
                other.priceVnd == priceVnd));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      name,
      category,
      quantity,
      unit,
      storageTier,
      source,
      ingredientId,
      packedDate,
      expiryDate,
      referenceShelfLifeDays,
      priceVnd);

  @override
  String toString() {
    return 'PantryItemDraft(name: $name, category: $category, quantity: $quantity, unit: $unit, storageTier: $storageTier, source: $source, ingredientId: $ingredientId, packedDate: $packedDate, expiryDate: $expiryDate, referenceShelfLifeDays: $referenceShelfLifeDays, priceVnd: $priceVnd)';
  }
}

/// @nodoc
abstract mixin class _$PantryItemDraftCopyWith<$Res>
    implements $PantryItemDraftCopyWith<$Res> {
  factory _$PantryItemDraftCopyWith(
          _PantryItemDraft value, $Res Function(_PantryItemDraft) _then) =
      __$PantryItemDraftCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String name,
      String category,
      double quantity,
      MeasurementUnit unit,
      StorageTier storageTier,
      PantrySource source,
      String? ingredientId,
      DateTime? packedDate,
      DateTime? expiryDate,
      int? referenceShelfLifeDays,
      int? priceVnd});
}

/// @nodoc
class __$PantryItemDraftCopyWithImpl<$Res>
    implements _$PantryItemDraftCopyWith<$Res> {
  __$PantryItemDraftCopyWithImpl(this._self, this._then);

  final _PantryItemDraft _self;
  final $Res Function(_PantryItemDraft) _then;

  /// Create a copy of PantryItemDraft
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? name = null,
    Object? category = null,
    Object? quantity = null,
    Object? unit = null,
    Object? storageTier = null,
    Object? source = null,
    Object? ingredientId = freezed,
    Object? packedDate = freezed,
    Object? expiryDate = freezed,
    Object? referenceShelfLifeDays = freezed,
    Object? priceVnd = freezed,
  }) {
    return _then(_PantryItemDraft(
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      category: null == category
          ? _self.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      quantity: null == quantity
          ? _self.quantity
          : quantity // ignore: cast_nullable_to_non_nullable
              as double,
      unit: null == unit
          ? _self.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as MeasurementUnit,
      storageTier: null == storageTier
          ? _self.storageTier
          : storageTier // ignore: cast_nullable_to_non_nullable
              as StorageTier,
      source: null == source
          ? _self.source
          : source // ignore: cast_nullable_to_non_nullable
              as PantrySource,
      ingredientId: freezed == ingredientId
          ? _self.ingredientId
          : ingredientId // ignore: cast_nullable_to_non_nullable
              as String?,
      packedDate: freezed == packedDate
          ? _self.packedDate
          : packedDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      expiryDate: freezed == expiryDate
          ? _self.expiryDate
          : expiryDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      referenceShelfLifeDays: freezed == referenceShelfLifeDays
          ? _self.referenceShelfLifeDays
          : referenceShelfLifeDays // ignore: cast_nullable_to_non_nullable
              as int?,
      priceVnd: freezed == priceVnd
          ? _self.priceVnd
          : priceVnd // ignore: cast_nullable_to_non_nullable
              as int?,
    ));
  }
}

// dart format on
