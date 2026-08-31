import 'package:permission_handler/permission_handler.dart' as ph;
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'permission_service.g.dart';

/// Wraps `permission_handler` for the Camera and Microphone permissions used by
/// the multimodal input flow (M4). Notification permission is handled in
/// `core/notifications/local_notifications.dart`.
class PermissionService {
  const PermissionService();

  Future<bool> hasCameraPermission() async =>
      (await ph.Permission.camera.status).isGranted;

  Future<bool> requestCameraPermission() async =>
      (await ph.Permission.camera.request()).isGranted;

  Future<bool> isCameraPermanentlyDenied() async =>
      (await ph.Permission.camera.status).isPermanentlyDenied;

  Future<bool> hasMicrophonePermission() async =>
      (await ph.Permission.microphone.status).isGranted;

  Future<bool> requestMicrophonePermission() async =>
      (await ph.Permission.microphone.request()).isGranted;

  Future<bool> isMicrophonePermanentlyDenied() async =>
      (await ph.Permission.microphone.status).isPermanentlyDenied;

  /// Opens the OS app-settings page (for a permanently denied permission).
  Future<bool> openSettings() => ph.openAppSettings();
}

@riverpod
PermissionService permissionService(Ref ref) => const PermissionService();
