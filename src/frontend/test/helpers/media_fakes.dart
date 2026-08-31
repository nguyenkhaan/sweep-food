// test/helpers/media_fakes.dart
// Test doubles for the M4 media / permission services (no platform channels).
import 'package:sweepfood/core/media/audio_recorder_service.dart';
import 'package:sweepfood/core/media/image_capture_service.dart';
import 'package:sweepfood/core/permissions/permission_service.dart';

/// Reports every permission as already granted.
class GrantedPermissionService extends PermissionService {
  const GrantedPermissionService();

  @override
  Future<bool> hasCameraPermission() async => true;
  @override
  Future<bool> requestCameraPermission() async => true;
  @override
  Future<bool> isCameraPermanentlyDenied() async => false;
  @override
  Future<bool> hasMicrophonePermission() async => true;
  @override
  Future<bool> requestMicrophonePermission() async => true;
  @override
  Future<bool> isMicrophonePermanentlyDenied() async => false;
  @override
  Future<bool> openSettings() async => true;
}

/// A recorder that "records" without touching the mic.
class FakeAudioRecorderService extends AudioRecorderService {
  FakeAudioRecorderService({this.canStart = true});

  final bool canStart;

  @override
  Future<bool> hasPermission() async => true;
  @override
  Future<bool> start() async => canStart;
  @override
  Future<String?> stop() async => canStart ? '/tmp/fake_voice.m4a' : null;
  @override
  Future<void> cancel() async {}
  @override
  Stream<double> amplitude({
    Duration interval = const Duration(milliseconds: 120),
  }) =>
      const Stream<double>.empty();
  @override
  Future<void> dispose() async {}
}

/// Returns a fixed path instead of opening the camera / gallery.
class FakeImageCaptureService extends ImageCaptureService {
  FakeImageCaptureService({this.path = '/tmp/fake_capture.jpg'});

  final String? path;

  @override
  Future<String?> capture({required ImageSource source, bool crop = false}) async =>
      path;
}
