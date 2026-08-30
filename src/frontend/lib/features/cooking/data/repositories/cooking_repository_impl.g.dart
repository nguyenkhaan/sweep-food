// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'cooking_repository_impl.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(cookingRepository)
final cookingRepositoryProvider = CookingRepositoryProvider._();

final class CookingRepositoryProvider extends $FunctionalProvider<
    CookingRepository,
    CookingRepository,
    CookingRepository> with $Provider<CookingRepository> {
  CookingRepositoryProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'cookingRepositoryProvider',
          isAutoDispose: false,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$cookingRepositoryHash();

  @$internal
  @override
  $ProviderElement<CookingRepository> $createElement(
          $ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  CookingRepository create(Ref ref) {
    return cookingRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(CookingRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<CookingRepository>(value),
    );
  }
}

String _$cookingRepositoryHash() => r'f7b4e43de72503ddaa19b4ff3931afdd74428c4c';
