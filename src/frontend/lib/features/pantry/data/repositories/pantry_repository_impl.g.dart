// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pantry_repository_impl.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(pantryRepository)
final pantryRepositoryProvider = PantryRepositoryProvider._();

final class PantryRepositoryProvider extends $FunctionalProvider<
    PantryRepository,
    PantryRepository,
    PantryRepository> with $Provider<PantryRepository> {
  PantryRepositoryProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'pantryRepositoryProvider',
          isAutoDispose: false,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$pantryRepositoryHash();

  @$internal
  @override
  $ProviderElement<PantryRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  PantryRepository create(Ref ref) {
    return pantryRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(PantryRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<PantryRepository>(value),
    );
  }
}

String _$pantryRepositoryHash() => r'bd005abf507037c5388826b2a07509404dc85874';
