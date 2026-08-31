import 'package:permission_handler/permission_handler.dart' as ph;
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'permission_service.g.dart';

/// Wraps `permission_handler` for the Camera and Microphone permissions used by
/// the multimodal input flow (M4). Notification permission is handled in
/// `core/notifications/local_notifications.dart`.
///
/// Every call is guarded: a missing plugin (widget tests) or a channel error
/// degrades to "not granted" instead of throwing out of the priming flow.
class PermissionService {
  const PermissionService();

  Future<bool> hasCameraPermission() => _isGranted(ph.Permission.camera);

  Future<bool> requestCameraPermission() => _request(ph.Permission.camera);

  Future<bool> isCameraPermanentlyDenied() =>
      _isPermanentlyDenied(ph.Permission.camera);

  Future<bool> hasMicrophonePermission() =>
      _isGranted(ph.Permission.microphone);

  Future<bool> requestMicrophonePermission() =>
      _request(ph.Permission.microphone);

  Future<bool> isMicrophonePermanentlyDenied() =>
      _isPermanentlyDenied(ph.Permission.microphone);

  /// Opens the OS app-settings page (for a permanently denied permission).
  Future<bool> openSettings() async {
    try {
      return await ph.openAppSettings();
    } on Object {
      return false;
    }
  }

  Future<bool> _isGranted(ph.Permission p) async {
    try {
      return (await p.status).isGranted;
    } on Object {
      return false;
    }
  }

  Future<bool> _request(ph.Permission p) async {
    try {
      return (await p.request()).isGranted;
    } on Object {
      return false;
    }
  }

  Future<bool> _isPermanentlyDenied(ph.Permission p) async {
    try {
      return (await p.status).isPermanentlyDenied;
    } on Object {
      return false;
    }
  }
}

@riverpod
PermissionService permissionService(Ref ref) => const PermissionService();
