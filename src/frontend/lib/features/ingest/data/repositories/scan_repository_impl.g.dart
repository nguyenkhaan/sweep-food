// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'scan_repository_impl.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(scanRepository)
final scanRepositoryProvider = ScanRepositoryProvider._();

final class ScanRepositoryProvider
    extends $FunctionalProvider<ScanRepository, ScanRepository, ScanRepository>
    with $Provider<ScanRepository> {
  ScanRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'scanRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$scanRepositoryHash();

  @$internal
  @override
  $ProviderElement<ScanRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  ScanRepository create(Ref ref) {
    return scanRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ScanRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ScanRepository>(value),
    );
  }
}

String _$scanRepositoryHash() => r'd3617ba37a431e8d83f8f88ce8cb49d541b91715';
