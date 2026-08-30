// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'leftover_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// D-06 — saves leftover portions as a new "Ăn liền" batch and refreshes the
/// pantry list. Kept alive: the saving sheet only `read`s this.

@ProviderFor(LeftoverController)
final leftoverControllerProvider = LeftoverControllerProvider._();

/// D-06 — saves leftover portions as a new "Ăn liền" batch and refreshes the
/// pantry list. Kept alive: the saving sheet only `read`s this.
final class LeftoverControllerProvider
    extends $AsyncNotifierProvider<LeftoverController, void> {
  /// D-06 — saves leftover portions as a new "Ăn liền" batch and refreshes the
  /// pantry list. Kept alive: the saving sheet only `read`s this.
  LeftoverControllerProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'leftoverControllerProvider',
          isAutoDispose: false,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$leftoverControllerHash();

  @$internal
  @override
  LeftoverController create() => LeftoverController();
}

String _$leftoverControllerHash() =>
    r'bf1f156e4223c89dd9a9bac531ee6450a041a477';

/// D-06 — saves leftover portions as a new "Ăn liền" batch and refreshes the
/// pantry list. Kept alive: the saving sheet only `read`s this.

abstract class _$LeftoverController extends $AsyncNotifier<void> {
  FutureOr<void> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<void>, void>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<AsyncValue<void>, void>,
        AsyncValue<void>,
        Object?,
        Object?>;
    element.handleCreate(ref, build);
  }
}
