import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:sweepfood/core/utils/logger.dart';

/// Records the microphone for voice ingestion (I-06).
///
/// Records a 16 kHz mono WAV that can be uploaded directly to the ASR service.
class AudioRecorderService {
  AudioRecorderService({AudioRecorder? recorder})
    : _recorder = recorder ?? AudioRecorder();

  final AudioRecorder _recorder;
  bool _recording = false;

  bool get isRecording => _recording;

  Future<bool> hasPermission() => _recorder.hasPermission();

  Future<bool> start() async {
    try {
      if (!await _recorder.hasPermission()) return false;
      final directory = await getTemporaryDirectory();
      final path =
          '${directory.path}/sweepfood_voice_'
          '${DateTime.now().millisecondsSinceEpoch}.wav';
      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 16000,
          numChannels: 1,
        ),
        path: path,
      );
      _recording = true;
      log.d('Voice capture started');
      return true;
    } on Object catch (error, stackTrace) {
      _recording = false;
      log.e(
        'Unable to start voice capture',
        error: error,
        stackTrace: stackTrace,
      );
      return false;
    }
  }

  Future<String?> stop() async {
    if (!_recording) return null;
    try {
      final path = await _recorder.stop();
      log.d('Voice capture stopped hasFile=${path?.isNotEmpty == true}');
      return path;
    } on Object catch (error, stackTrace) {
      log.e(
        'Unable to stop voice capture',
        error: error,
        stackTrace: stackTrace,
      );
      return null;
    } finally {
      _recording = false;
    }
  }

  Future<void> cancel() async {
    try {
      await _recorder.cancel();
    } finally {
      _recording = false;
    }
  }

  Stream<double> amplitude({
    Duration interval = const Duration(milliseconds: 120),
  }) => _recorder
      .onAmplitudeChanged(interval)
      .map((value) => ((value.current + 60) / 60).clamp(0.0, 1.0));

  Future<void> dispose() => _recorder.dispose();
}
