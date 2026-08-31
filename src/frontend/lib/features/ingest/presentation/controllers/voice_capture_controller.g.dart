// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'voice_capture_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(VoiceCaptureController)
final voiceCaptureControllerProvider = VoiceCaptureControllerProvider._();

final class VoiceCaptureControllerProvider
    extends $NotifierProvider<VoiceCaptureController, VoiceCaptureState> {
  VoiceCaptureControllerProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'voiceCaptureControllerProvider',
          isAutoDispose: true,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$voiceCaptureControllerHash();

  @$internal
  @override
  VoiceCaptureController create() => VoiceCaptureController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(VoiceCaptureState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<VoiceCaptureState>(value),
    );
  }
}

String _$voiceCaptureControllerHash() =>
    r'0532d57de718397e47ba236223847571968d8ca5';

abstract class _$VoiceCaptureController extends $Notifier<VoiceCaptureState> {
  VoiceCaptureState build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<VoiceCaptureState, VoiceCaptureState>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<VoiceCaptureState, VoiceCaptureState>,
        VoiceCaptureState,
        Object?,
        Object?>;
    element.handleCreate(ref, build);
  }
}
