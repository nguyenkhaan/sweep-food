// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'media_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Camera / gallery capture (+ crop) — see [ImageCaptureService].

@ProviderFor(imageCaptureService)
final imageCaptureServiceProvider = ImageCaptureServiceProvider._();

/// Camera / gallery capture (+ crop) — see [ImageCaptureService].

final class ImageCaptureServiceProvider
    extends
        $FunctionalProvider<
          ImageCaptureService,
          ImageCaptureService,
          ImageCaptureService
        >
    with $Provider<ImageCaptureService> {
  /// Camera / gallery capture (+ crop) — see [ImageCaptureService].
  ImageCaptureServiceProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'imageCaptureServiceProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$imageCaptureServiceHash();

  @$internal
  @override
  $ProviderElement<ImageCaptureService> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  ImageCaptureService create(Ref ref) {
    return imageCaptureService(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ImageCaptureService value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ImageCaptureService>(value),
    );
  }
}

String _$imageCaptureServiceHash() =>
    r'f9fcbd0029a1da7aa4f56ace5a7ccdabebd540b4';

/// Mic recording for voice ingestion — see [AudioRecorderService].
/// Kept alive so one recorder instance owns the native session; disposed with
/// the provider container.

@ProviderFor(audioRecorderService)
final audioRecorderServiceProvider = AudioRecorderServiceProvider._();

/// Mic recording for voice ingestion — see [AudioRecorderService].
/// Kept alive so one recorder instance owns the native session; disposed with
/// the provider container.

final class AudioRecorderServiceProvider
    extends
        $FunctionalProvider<
          AudioRecorderService,
          AudioRecorderService,
          AudioRecorderService
        >
    with $Provider<AudioRecorderService> {
  /// Mic recording for voice ingestion — see [AudioRecorderService].
  /// Kept alive so one recorder instance owns the native session; disposed with
  /// the provider container.
  AudioRecorderServiceProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'audioRecorderServiceProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$audioRecorderServiceHash();

  @$internal
  @override
  $ProviderElement<AudioRecorderService> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  AudioRecorderService create(Ref ref) {
    return audioRecorderService(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AudioRecorderService value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AudioRecorderService>(value),
    );
  }
}

String _$audioRecorderServiceHash() =>
    r'c7c47b9006d195cb7502643cc627899e8dd6c881';
