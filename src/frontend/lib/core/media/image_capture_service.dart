import 'package:image_cropper/image_cropper.dart';
import 'package:image_picker/image_picker.dart';

export 'package:image_picker/image_picker.dart' show ImageSource;

/// Thin wrapper over `image_picker` (+ `image_cropper` for I-02) so the camera
/// screen depends on an interface instead of the plugins directly. Every call
/// returns a local file path or `null` when the user backs out / the plugin
/// isn't available on this platform.
class ImageCaptureService {
  ImageCaptureService({ImagePicker? picker, ImageCropper? cropper})
      : _picker = picker ?? ImagePicker(),
        _cropper = cropper ?? ImageCropper();

  final ImagePicker _picker;
  final ImageCropper _cropper;

  /// Take a photo (`ImageSource.camera`) or pick one (`ImageSource.gallery`),
  /// optionally routing it through the crop UI first (I-02).
  ///
  /// Returns `null` only when the user backs out. A real plugin failure
  /// (no camera, permission missing, channel error) is **thrown** so the
  /// caller can surface it instead of silently doing nothing.
  Future<String?> capture({
    required ImageSource source,
    bool crop = false,
  }) async {
    final picked = await _picker.pickImage(
      source: source,
      imageQuality: 85,
      maxWidth: 2400,
    );
    if (picked == null) return null;
    if (!crop) return picked.path;
    return _crop(picked.path);
  }

  /// Crop is best-effort — if the crop UI isn't available on this build
  /// (e.g. `UCropActivity` not declared, deferred to M6) fall back to the
  /// uncropped image rather than failing the whole capture.
  Future<String?> _crop(String path) async {
    try {
      final cropped = await _cropper.cropImage(
        sourcePath: path,
        compressQuality: 90,
      );
      return cropped?.path ?? path;
    } on Exception {
      return path;
    }
  }
}
