import 'package:frontend/core/media/audio_recorder_service.dart';
import 'package:frontend/core/media/image_capture_service.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'media_providers.g.dart';

/// Camera / gallery capture (+ crop) — see [ImageCaptureService].
@riverpod
ImageCaptureService imageCaptureService(Ref ref) => ImageCaptureService();

/// Mic recording for voice ingestion — see [AudioRecorderService].
/// Kept alive so one recorder instance owns the native session; disposed with
/// the provider container.
@Riverpod(keepAlive: true)
AudioRecorderService audioRecorderService(Ref ref) {
  final service = AudioRecorderService();
  ref.onDispose(service.dispose);
  return service;
}
