// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dish_repository_impl.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(dishRepository)
final dishRepositoryProvider = DishRepositoryProvider._();

final class DishRepositoryProvider
    extends $FunctionalProvider<DishRepository, DishRepository, DishRepository>
    with $Provider<DishRepository> {
  DishRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'dishRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$dishRepositoryHash();

  @$internal
  @override
  $ProviderElement<DishRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  DishRepository create(Ref ref) {
    return dishRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(DishRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<DishRepository>(value),
    );
  }
}

String _$dishRepositoryHash() => r'd7904ed163bde5a5193455985cd06bfee53d5937';
