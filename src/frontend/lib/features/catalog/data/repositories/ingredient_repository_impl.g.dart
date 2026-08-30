// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ingredient_repository_impl.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(ingredientRepository)
final ingredientRepositoryProvider = IngredientRepositoryProvider._();

final class IngredientRepositoryProvider extends $FunctionalProvider<
    IngredientRepository,
    IngredientRepository,
    IngredientRepository> with $Provider<IngredientRepository> {
  IngredientRepositoryProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'ingredientRepositoryProvider',
          isAutoDispose: false,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$ingredientRepositoryHash();

  @$internal
  @override
  $ProviderElement<IngredientRepository> $createElement(
          $ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  IngredientRepository create(Ref ref) {
    return ingredientRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(IngredientRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<IngredientRepository>(value),
    );
  }
}

String _$ingredientRepositoryHash() =>
    r'ae7ea4429bbbf749b1631f951c91c3744f9c34c9';
