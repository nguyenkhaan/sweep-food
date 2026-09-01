// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'voice_capture_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(VoiceCaptureController)
final voiceCaptureControllerProvider = VoiceCaptureControllerFamily._();

final class VoiceCaptureControllerProvider
    extends $NotifierProvider<VoiceCaptureController, VoiceReviewState> {
  VoiceCaptureControllerProvider._({
    required VoiceCaptureControllerFamily super.from,
    required ScanJob super.argument,
  }) : super(
         retry: null,
         name: r'voiceCaptureControllerProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$voiceCaptureControllerHash();

  @override
  String toString() {
    return r'voiceCaptureControllerProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  VoiceCaptureController create() => VoiceCaptureController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(VoiceReviewState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<VoiceReviewState>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is VoiceCaptureControllerProvider &&
        other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$voiceCaptureControllerHash() =>
    r'a2ccc9b9f2c56877c47b91ebeb388a28c1efda3c';

final class VoiceCaptureControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          VoiceCaptureController,
          VoiceReviewState,
          VoiceReviewState,
          VoiceReviewState,
          ScanJob
        > {
  VoiceCaptureControllerFamily._()
    : super(
        retry: null,
        name: r'voiceCaptureControllerProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  VoiceCaptureControllerProvider call(ScanJob job) =>
      VoiceCaptureControllerProvider._(argument: job, from: this);

  @override
  String toString() => r'voiceCaptureControllerProvider';
}

abstract class _$VoiceCaptureController extends $Notifier<VoiceReviewState> {
  late final _$args = ref.$arg as ScanJob;
  ScanJob get job => _$args;

  VoiceReviewState build(ScanJob job);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<VoiceReviewState, VoiceReviewState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<VoiceReviewState, VoiceReviewState>,
              VoiceReviewState,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
