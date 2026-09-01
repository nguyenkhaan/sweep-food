import 'dart:async';
import 'dart:math' as math;

/// Records the microphone for voice ingestion (I-06).
///
/// The real capture path is built on the `record` plugin and lives behind this
/// class's API (`start` / `stop` / [amplitude]). It is currently **disabled**:
/// the plugin version available in this workspace ships a `record_web` that does
/// not compile against `record_platform_interface >= 1.5.0`, which breaks
/// `flutter build web`. Until the plugin stack realigns, this stub keeps the
/// flow working end-to-end — [start] reports failure, so `VoiceCaptureScreen`
/// falls back to the canned ASR result — while [amplitude] still emits a gentle
/// synthetic level so the waveform reads as "listening".
///
/// To re-enable: add `record` back to `pubspec.yaml`, then swap the bodies below
/// for `AudioRecorder()` calls (`hasPermission` / `start(RecordConfig(), path:)`
/// / `stop` / `onAmplitudeChanged`).
class AudioRecorderService {
  AudioRecorderService();

  bool _recording = false;

  bool get isRecording => _recording;

  Future<bool> hasPermission() async => false;

  /// Returns `false` — real recording is disabled (see class docs).
  Future<bool> start() async {
    _recording = false;
    return false;
  }

  Future<String?> stop() async {
    _recording = false;
    return null;
  }

  Future<void> cancel() async {
    _recording = false;
  }

  /// A slow synthetic 0.0–1.0 level so the visualizer animates while the user
  /// speaks, even though no audio is captured.
  Stream<double> amplitude({
    Duration interval = const Duration(milliseconds: 120),
  }) async* {
    var t = 0.0;
    while (true) {
      await Future<void>.delayed(interval);
      t += 0.35;
      yield (0.28 + 0.22 * math.sin(t) + 0.12 * math.sin(t * 2.7))
          .clamp(0.05, 1.0);
    }
  }

  Future<void> dispose() async {}
}
