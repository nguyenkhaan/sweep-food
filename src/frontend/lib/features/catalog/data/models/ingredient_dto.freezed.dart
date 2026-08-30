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
  String get id;
  String get name;
  String get category;
  @JsonKey(name: 'default_unit')
  String get defaultUnit;
  @JsonKey(name: 'nutrition_per_100g')
  NutritionPer100gDto? get nutritionPer100g;
  @JsonKey(name: 'reference_shelf_life_days')
  int? get referenceShelfLifeDays;

  /// Create a copy of IngredientDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $IngredientDtoCopyWith<IngredientDto> get copyWith =>
      _$IngredientDtoCopyWithImpl<IngredientDto>(
          this as IngredientDto, _$identity);

  /// Serializes this IngredientDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is IngredientDto &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.defaultUnit, defaultUnit) ||
                other.defaultUnit == defaultUnit) &&
            (identical(other.nutritionPer100g, nutritionPer100g) ||
                other.nutritionPer100g == nutritionPer100g) &&
            (identical(other.referenceShelfLifeDays, referenceShelfLifeDays) ||
                other.referenceShelfLifeDays == referenceShelfLifeDays));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, name, category, defaultUnit,
      nutritionPer100g, referenceShelfLifeDays);

  @override
  String toString() {
    return 'IngredientDto(id: $id, name: $name, category: $category, defaultUnit: $defaultUnit, nutritionPer100g: $nutritionPer100g, referenceShelfLifeDays: $referenceShelfLifeDays)';
  }
}

/// @nodoc
abstract mixin class $IngredientDtoCopyWith<$Res> {
  factory $IngredientDtoCopyWith(
          IngredientDto value, $Res Function(IngredientDto) _then) =
      _$IngredientDtoCopyWithImpl;
  @useResult
  $Res call(
      {String id,
      String name,
      String category,
      @JsonKey(name: 'default_unit') String defaultUnit,
      @JsonKey(name: 'nutrition_per_100g')
      NutritionPer100gDto? nutritionPer100g,
      @JsonKey(name: 'reference_shelf_life_days') int? referenceShelfLifeDays});

  $NutritionPer100gDtoCopyWith<$Res>? get nutritionPer100g;
}

/// @nodoc
class _$IngredientDtoCopyWithImpl<$Res>
    implements $IngredientDtoCopyWith<$Res> {
  _$IngredientDtoCopyWithImpl(this._self, this._then);

  final IngredientDto _self;
  final $Res Function(IngredientDto) _then;

  /// Create a copy of IngredientDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? category = null,
    Object? defaultUnit = null,
    Object? nutritionPer100g = freezed,
    Object? referenceShelfLifeDays = freezed,
  }) {
    return _then(_self.copyWith(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      category: null == category
          ? _self.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      defaultUnit: null == defaultUnit
          ? _self.defaultUnit
          : defaultUnit // ignore: cast_nullable_to_non_nullable
              as String,
      nutritionPer100g: freezed == nutritionPer100g
          ? _self.nutritionPer100g
          : nutritionPer100g // ignore: cast_nullable_to_non_nullable
              as NutritionPer100gDto?,
      referenceShelfLifeDays: freezed == referenceShelfLifeDays
          ? _self.referenceShelfLifeDays
          : referenceShelfLifeDays // ignore: cast_nullable_to_non_nullable
              as int?,
    ));
  }

  /// Create a copy of IngredientDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $NutritionPer100gDtoCopyWith<$Res>? get nutritionPer100g {
    if (_self.nutritionPer100g == null) {
      return null;
    }

    return $NutritionPer100gDtoCopyWith<$Res>(_self.nutritionPer100g!, (value) {
      return _then(_self.copyWith(nutritionPer100g: value));
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

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>(
    TResult Function(_IngredientDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _IngredientDto() when $default != null:
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
    TResult Function(_IngredientDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _IngredientDto():
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
    TResult? Function(_IngredientDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _IngredientDto() when $default != null:
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
            String id,
            String name,
            String category,
            @JsonKey(name: 'default_unit') String defaultUnit,
            @JsonKey(name: 'nutrition_per_100g')
            NutritionPer100gDto? nutritionPer100g,
            @JsonKey(name: 'reference_shelf_life_days')
            int? referenceShelfLifeDays)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _IngredientDto() when $default != null:
        return $default(_that.id, _that.name, _that.category, _that.defaultUnit,
            _that.nutritionPer100g, _that.referenceShelfLifeDays);
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
            String id,
            String name,
            String category,
            @JsonKey(name: 'default_unit') String defaultUnit,
            @JsonKey(name: 'nutrition_per_100g')
            NutritionPer100gDto? nutritionPer100g,
            @JsonKey(name: 'reference_shelf_life_days')
            int? referenceShelfLifeDays)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _IngredientDto():
        return $default(_that.id, _that.name, _that.category, _that.defaultUnit,
            _that.nutritionPer100g, _that.referenceShelfLifeDays);
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
            String id,
            String name,
            String category,
            @JsonKey(name: 'default_unit') String defaultUnit,
            @JsonKey(name: 'nutrition_per_100g')
            NutritionPer100gDto? nutritionPer100g,
            @JsonKey(name: 'reference_shelf_life_days')
            int? referenceShelfLifeDays)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _IngredientDto() when $default != null:
        return $default(_that.id, _that.name, _that.category, _that.defaultUnit,
            _that.nutritionPer100g, _that.referenceShelfLifeDays);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _IngredientDto extends IngredientDto {
  const _IngredientDto(
      {required this.id,
      required this.name,
      required this.category,
      @JsonKey(name: 'default_unit') this.defaultUnit = 'g',
      @JsonKey(name: 'nutrition_per_100g') this.nutritionPer100g,
      @JsonKey(name: 'reference_shelf_life_days') this.referenceShelfLifeDays})
      : super._();
  factory _IngredientDto.fromJson(Map<String, dynamic> json) =>
      _$IngredientDtoFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String category;
  @override
  @JsonKey(name: 'default_unit')
  final String defaultUnit;
  @override
  @JsonKey(name: 'nutrition_per_100g')
  final NutritionPer100gDto? nutritionPer100g;
  @override
  @JsonKey(name: 'reference_shelf_life_days')
  final int? referenceShelfLifeDays;

  /// Create a copy of IngredientDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$IngredientDtoCopyWith<_IngredientDto> get copyWith =>
      __$IngredientDtoCopyWithImpl<_IngredientDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$IngredientDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _IngredientDto &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.defaultUnit, defaultUnit) ||
                other.defaultUnit == defaultUnit) &&
            (identical(other.nutritionPer100g, nutritionPer100g) ||
                other.nutritionPer100g == nutritionPer100g) &&
            (identical(other.referenceShelfLifeDays, referenceShelfLifeDays) ||
                other.referenceShelfLifeDays == referenceShelfLifeDays));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, name, category, defaultUnit,
      nutritionPer100g, referenceShelfLifeDays);

  @override
  String toString() {
    return 'IngredientDto(id: $id, name: $name, category: $category, defaultUnit: $defaultUnit, nutritionPer100g: $nutritionPer100g, referenceShelfLifeDays: $referenceShelfLifeDays)';
  }
}

/// @nodoc
abstract mixin class _$IngredientDtoCopyWith<$Res>
    implements $IngredientDtoCopyWith<$Res> {
  factory _$IngredientDtoCopyWith(
          _IngredientDto value, $Res Function(_IngredientDto) _then) =
      __$IngredientDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String category,
      @JsonKey(name: 'default_unit') String defaultUnit,
      @JsonKey(name: 'nutrition_per_100g')
      NutritionPer100gDto? nutritionPer100g,
      @JsonKey(name: 'reference_shelf_life_days') int? referenceShelfLifeDays});

  @override
  $NutritionPer100gDtoCopyWith<$Res>? get nutritionPer100g;
}

/// @nodoc
class __$IngredientDtoCopyWithImpl<$Res>
    implements _$IngredientDtoCopyWith<$Res> {
  __$IngredientDtoCopyWithImpl(this._self, this._then);

  final _IngredientDto _self;
  final $Res Function(_IngredientDto) _then;

  /// Create a copy of IngredientDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? category = null,
    Object? defaultUnit = null,
    Object? nutritionPer100g = freezed,
    Object? referenceShelfLifeDays = freezed,
  }) {
    return _then(_IngredientDto(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      category: null == category
          ? _self.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      defaultUnit: null == defaultUnit
          ? _self.defaultUnit
          : defaultUnit // ignore: cast_nullable_to_non_nullable
              as String,
      nutritionPer100g: freezed == nutritionPer100g
          ? _self.nutritionPer100g
          : nutritionPer100g // ignore: cast_nullable_to_non_nullable
              as NutritionPer100gDto?,
      referenceShelfLifeDays: freezed == referenceShelfLifeDays
          ? _self.referenceShelfLifeDays
          : referenceShelfLifeDays // ignore: cast_nullable_to_non_nullable
              as int?,
    ));
  }

  /// Create a copy of IngredientDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $NutritionPer100gDtoCopyWith<$Res>? get nutritionPer100g {
    if (_self.nutritionPer100g == null) {
      return null;
    }

    return $NutritionPer100gDtoCopyWith<$Res>(_self.nutritionPer100g!, (value) {
      return _then(_self.copyWith(nutritionPer100g: value));
    });
  }
}

/// @nodoc
mixin _$NutritionPer100gDto {
  @JsonKey(name: 'energy_kcal')
  double get energyKcal;
  @JsonKey(name: 'protein_g')
  double get proteinG;
  @JsonKey(name: 'carb_g')
  double get carbG;
  @JsonKey(name: 'lipid_g')
  double get lipidG;

  /// Create a copy of NutritionPer100gDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $NutritionPer100gDtoCopyWith<NutritionPer100gDto> get copyWith =>
      _$NutritionPer100gDtoCopyWithImpl<NutritionPer100gDto>(
          this as NutritionPer100gDto, _$identity);

  /// Serializes this NutritionPer100gDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is NutritionPer100gDto &&
            (identical(other.energyKcal, energyKcal) ||
                other.energyKcal == energyKcal) &&
            (identical(other.proteinG, proteinG) ||
                other.proteinG == proteinG) &&
            (identical(other.carbG, carbG) || other.carbG == carbG) &&
            (identical(other.lipidG, lipidG) || other.lipidG == lipidG));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, energyKcal, proteinG, carbG, lipidG);

  @override
  String toString() {
    return 'NutritionPer100gDto(energyKcal: $energyKcal, proteinG: $proteinG, carbG: $carbG, lipidG: $lipidG)';
  }
}

/// @nodoc
abstract mixin class $NutritionPer100gDtoCopyWith<$Res> {
  factory $NutritionPer100gDtoCopyWith(
          NutritionPer100gDto value, $Res Function(NutritionPer100gDto) _then) =
      _$NutritionPer100gDtoCopyWithImpl;
  @useResult
  $Res call(
      {@JsonKey(name: 'energy_kcal') double energyKcal,
      @JsonKey(name: 'protein_g') double proteinG,
      @JsonKey(name: 'carb_g') double carbG,
      @JsonKey(name: 'lipid_g') double lipidG});
}

/// @nodoc
class _$NutritionPer100gDtoCopyWithImpl<$Res>
    implements $NutritionPer100gDtoCopyWith<$Res> {
  _$NutritionPer100gDtoCopyWithImpl(this._self, this._then);

  final NutritionPer100gDto _self;
  final $Res Function(NutritionPer100gDto) _then;

  /// Create a copy of NutritionPer100gDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? energyKcal = null,
    Object? proteinG = null,
    Object? carbG = null,
    Object? lipidG = null,
  }) {
    return _then(_self.copyWith(
      energyKcal: null == energyKcal
          ? _self.energyKcal
          : energyKcal // ignore: cast_nullable_to_non_nullable
              as double,
      proteinG: null == proteinG
          ? _self.proteinG
          : proteinG // ignore: cast_nullable_to_non_nullable
              as double,
      carbG: null == carbG
          ? _self.carbG
          : carbG // ignore: cast_nullable_to_non_nullable
              as double,
      lipidG: null == lipidG
          ? _self.lipidG
          : lipidG // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// Adds pattern-matching-related methods to [NutritionPer100gDto].
extension NutritionPer100gDtoPatterns on NutritionPer100gDto {
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
    TResult Function(_NutritionPer100gDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _NutritionPer100gDto() when $default != null:
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
    TResult Function(_NutritionPer100gDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _NutritionPer100gDto():
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
    TResult? Function(_NutritionPer100gDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _NutritionPer100gDto() when $default != null:
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
            @JsonKey(name: 'energy_kcal') double energyKcal,
            @JsonKey(name: 'protein_g') double proteinG,
            @JsonKey(name: 'carb_g') double carbG,
            @JsonKey(name: 'lipid_g') double lipidG)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _NutritionPer100gDto() when $default != null:
        return $default(
            _that.energyKcal, _that.proteinG, _that.carbG, _that.lipidG);
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
            @JsonKey(name: 'energy_kcal') double energyKcal,
            @JsonKey(name: 'protein_g') double proteinG,
            @JsonKey(name: 'carb_g') double carbG,
            @JsonKey(name: 'lipid_g') double lipidG)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _NutritionPer100gDto():
        return $default(
            _that.energyKcal, _that.proteinG, _that.carbG, _that.lipidG);
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
            @JsonKey(name: 'energy_kcal') double energyKcal,
            @JsonKey(name: 'protein_g') double proteinG,
            @JsonKey(name: 'carb_g') double carbG,
            @JsonKey(name: 'lipid_g') double lipidG)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _NutritionPer100gDto() when $default != null:
        return $default(
            _that.energyKcal, _that.proteinG, _that.carbG, _that.lipidG);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _NutritionPer100gDto extends NutritionPer100gDto {
  const _NutritionPer100gDto(
      {@JsonKey(name: 'energy_kcal') this.energyKcal = 0,
      @JsonKey(name: 'protein_g') this.proteinG = 0,
      @JsonKey(name: 'carb_g') this.carbG = 0,
      @JsonKey(name: 'lipid_g') this.lipidG = 0})
      : super._();
  factory _NutritionPer100gDto.fromJson(Map<String, dynamic> json) =>
      _$NutritionPer100gDtoFromJson(json);

  @override
  @JsonKey(name: 'energy_kcal')
  final double energyKcal;
  @override
  @JsonKey(name: 'protein_g')
  final double proteinG;
  @override
  @JsonKey(name: 'carb_g')
  final double carbG;
  @override
  @JsonKey(name: 'lipid_g')
  final double lipidG;

  /// Create a copy of NutritionPer100gDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$NutritionPer100gDtoCopyWith<_NutritionPer100gDto> get copyWith =>
      __$NutritionPer100gDtoCopyWithImpl<_NutritionPer100gDto>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$NutritionPer100gDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _NutritionPer100gDto &&
            (identical(other.energyKcal, energyKcal) ||
                other.energyKcal == energyKcal) &&
            (identical(other.proteinG, proteinG) ||
                other.proteinG == proteinG) &&
            (identical(other.carbG, carbG) || other.carbG == carbG) &&
            (identical(other.lipidG, lipidG) || other.lipidG == lipidG));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, energyKcal, proteinG, carbG, lipidG);

  @override
  String toString() {
    return 'NutritionPer100gDto(energyKcal: $energyKcal, proteinG: $proteinG, carbG: $carbG, lipidG: $lipidG)';
  }
}

/// @nodoc
abstract mixin class _$NutritionPer100gDtoCopyWith<$Res>
    implements $NutritionPer100gDtoCopyWith<$Res> {
  factory _$NutritionPer100gDtoCopyWith(_NutritionPer100gDto value,
          $Res Function(_NutritionPer100gDto) _then) =
      __$NutritionPer100gDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'energy_kcal') double energyKcal,
      @JsonKey(name: 'protein_g') double proteinG,
      @JsonKey(name: 'carb_g') double carbG,
      @JsonKey(name: 'lipid_g') double lipidG});
}

/// @nodoc
class __$NutritionPer100gDtoCopyWithImpl<$Res>
    implements _$NutritionPer100gDtoCopyWith<$Res> {
  __$NutritionPer100gDtoCopyWithImpl(this._self, this._then);

  final _NutritionPer100gDto _self;
  final $Res Function(_NutritionPer100gDto) _then;

  /// Create a copy of NutritionPer100gDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? energyKcal = null,
    Object? proteinG = null,
    Object? carbG = null,
    Object? lipidG = null,
  }) {
    return _then(_NutritionPer100gDto(
      energyKcal: null == energyKcal
          ? _self.energyKcal
          : energyKcal // ignore: cast_nullable_to_non_nullable
              as double,
      proteinG: null == proteinG
          ? _self.proteinG
          : proteinG // ignore: cast_nullable_to_non_nullable
              as double,
      carbG: null == carbG
          ? _self.carbG
          : carbG // ignore: cast_nullable_to_non_nullable
              as double,
      lipidG: null == lipidG
          ? _self.lipidG
          : lipidG // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

// dart format on
