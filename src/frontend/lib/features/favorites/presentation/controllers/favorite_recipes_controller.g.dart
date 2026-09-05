// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'favorite_recipes_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(FavoriteRecipesController)
final favoriteRecipesControllerProvider = FavoriteRecipesControllerProvider._();

final class FavoriteRecipesControllerProvider
    extends
        $AsyncNotifierProvider<
          FavoriteRecipesController,
          List<FavoriteRecipe>
        > {
  FavoriteRecipesControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'favoriteRecipesControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$favoriteRecipesControllerHash();

  @$internal
  @override
  FavoriteRecipesController create() => FavoriteRecipesController();
}

String _$favoriteRecipesControllerHash() =>
    r'29d89c2d8b36e2a501d1b139b3e6b51124820a10';

abstract class _$FavoriteRecipesController
    extends $AsyncNotifier<List<FavoriteRecipe>> {
  FutureOr<List<FavoriteRecipe>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<AsyncValue<List<FavoriteRecipe>>, List<FavoriteRecipe>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<FavoriteRecipe>>,
                List<FavoriteRecipe>
              >,
              AsyncValue<List<FavoriteRecipe>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

@ProviderFor(isRecipeFavorite)
final isRecipeFavoriteProvider = IsRecipeFavoriteFamily._();

final class IsRecipeFavoriteProvider
    extends $FunctionalProvider<bool, bool, bool>
    with $Provider<bool> {
  IsRecipeFavoriteProvider._({
    required IsRecipeFavoriteFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'isRecipeFavoriteProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$isRecipeFavoriteHash();

  @override
  String toString() {
    return r'isRecipeFavoriteProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $ProviderElement<bool> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  bool create(Ref ref) {
    final argument = this.argument as String;
    return isRecipeFavorite(ref, argument);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(bool value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<bool>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is IsRecipeFavoriteProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$isRecipeFavoriteHash() => r'd74662b04f25d4a32fe47437dd809217fefb5fab';

final class IsRecipeFavoriteFamily extends $Family
    with $FunctionalFamilyOverride<bool, String> {
  IsRecipeFavoriteFamily._()
    : super(
        retry: null,
        name: r'isRecipeFavoriteProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  IsRecipeFavoriteProvider call(String recipeId) =>
      IsRecipeFavoriteProvider._(argument: recipeId, from: this);

  @override
  String toString() => r'isRecipeFavoriteProvider';
}
