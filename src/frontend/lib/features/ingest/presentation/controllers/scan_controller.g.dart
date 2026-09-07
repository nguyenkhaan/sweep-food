// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'scan_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Drives one capture → upload → extract cycle. The camera / voice screens
/// `read` this to run a scan and watch it for the in-flight state; the review
/// screens receive the resulting [ScanJob] via router `extra`.

@ProviderFor(ScanController)
final scanControllerProvider = ScanControllerProvider._();

/// Drives one capture → upload → extract cycle. The camera / voice screens
/// `read` this to run a scan and watch it for the in-flight state; the review
/// screens receive the resulting [ScanJob] via router `extra`.
final class ScanControllerProvider
    extends $AsyncNotifierProvider<ScanController, ScanJob?> {
  /// Drives one capture → upload → extract cycle. The camera / voice screens
  /// `read` this to run a scan and watch it for the in-flight state; the review
  /// screens receive the resulting [ScanJob] via router `extra`.
  ScanControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'scanControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$scanControllerHash();

  @$internal
  @override
  ScanController create() => ScanController();
}

String _$scanControllerHash() => r'587483e0f60ca9c7d182c3b2c592f3091aa024a6';

/// Drives one capture → upload → extract cycle. The camera / voice screens
/// `read` this to run a scan and watch it for the in-flight state; the review
/// screens receive the resulting [ScanJob] via router `extra`.

abstract class _$ScanController extends $AsyncNotifier<ScanJob?> {
  FutureOr<ScanJob?> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<ScanJob?>, ScanJob?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<ScanJob?>, ScanJob?>,
              AsyncValue<ScanJob?>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
