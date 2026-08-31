// lib/features/ingest/presentation/screens/camera_capture_screen.dart
// I-01 Quét tem nhãn & I-04 Quét hóa đơn
// Design: CameraCapture.dc.html

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/media/image_capture_service.dart';
import 'package:frontend/core/media/media_providers.dart';
import 'package:frontend/core/permissions/permission_prime_sheet.dart';
import 'package:frontend/core/permissions/permission_service.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/features/ingest/domain/entities/scan_type.dart';
import 'package:frontend/features/ingest/presentation/controllers/scan_controller.dart';
import 'package:frontend/features/ingest/presentation/widgets/viewfinder_overlay.dart';
import 'package:go_router/go_router.dart';

enum CameraScanMode {
  label('Tem nhãn', ScanType.label),
  receipt('Hóa đơn', ScanType.receipt);

  const CameraScanMode(this.title, this.scanType);

  final String title;
  final ScanType scanType;
}

/// I-01 / I-04 — khung ngắm camera trực tiếp trong app; nút trắng chụp lại
/// khung hình hiện tại rồi gửi OCR (không mở app máy ảnh của hệ thống).
class CameraCaptureScreen extends ConsumerStatefulWidget {
  const CameraCaptureScreen({this.initialMode = CameraScanMode.label, super.key});

  final CameraScanMode initialMode;

  @override
  ConsumerState<CameraCaptureScreen> createState() =>
      _CameraCaptureScreenState();
}

class _CameraCaptureScreenState extends ConsumerState<CameraCaptureScreen>
    with WidgetsBindingObserver {
  late CameraScanMode _mode = widget.initialMode;
  CameraController? _controller;
  bool _torch = false;
  bool _busy = false;

  /// `null` while starting / when the preview is live;
  /// `'permission'` when the OS permission was refused;
  /// any other string is a start-up error to show with a retry.
  String? _hint = _kStarting;
  static const _kStarting = '__starting__';

  bool get _previewReady =>
      _controller != null && _controller!.value.isInitialized;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    WidgetsBinding.instance.addPostFrameCallback((_) => _start());
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _controller?.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final c = _controller;
    if (state == AppLifecycleState.inactive ||
        state == AppLifecycleState.paused) {
      _controller = null;
      c?.dispose();
      if (mounted) setState(() => _hint = _kStarting);
    } else if (state == AppLifecycleState.resumed && c == null) {
      _start();
    }
  }

  Future<void> _start() async {
    final perms = ref.read(permissionServiceProvider);
    final alreadyGranted = await perms.hasCameraPermission();
    if (!mounted) return;
    if (!alreadyGranted) {
      final ok = await ensureMediaPermission(
        context,
        ref,
        PermissionKind.camera,
      );
      if (!mounted) return;
      if (!ok) {
        setState(() => _hint = 'permission');
        return;
      }
    }
    await _openCamera();
  }

  Future<void> _openCamera() async {
    try {
      final cams = await availableCameras();
      if (cams.isEmpty) {
        if (mounted) setState(() => _hint = 'Thiết bị không có máy ảnh.');
        return;
      }
      final back = cams.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.back,
        orElse: () => cams.first,
      );
      final controller = CameraController(
        back,
        ResolutionPreset.high,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.jpeg,
      );
      await controller.initialize();
      if (!mounted) {
        await controller.dispose();
        return;
      }
      setState(() {
        _controller = controller;
        _torch = false;
        _hint = null;
      });
    } on Object catch (e) {
      if (mounted) setState(() => _hint = 'Không mở được máy ảnh: $e');
    }
  }

  void _snack(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  Future<void> _toggleTorch() async {
    final c = _controller;
    if (c == null || !c.value.isInitialized) return;
    try {
      await c.setFlashMode(_torch ? FlashMode.off : FlashMode.torch);
      if (mounted) setState(() => _torch = !_torch);
    } on Object {
      _snack('Đèn flash không khả dụng trên thiết bị này.');
    }
  }

  Future<void> _shoot() async {
    final c = _controller;
    if (_busy || c == null || !c.value.isInitialized || c.value.isTakingPicture) {
      return;
    }
    setState(() => _busy = true);
    try {
      final shot = await c.takePicture();
      await _process(shot.path);
    } on Object catch (e) {
      if (mounted) {
        setState(() => _busy = false);
        _snack('Không chụp được: $e');
      }
    }
  }

  Future<void> _pickFromGallery() async {
    if (_busy) return;
    String? path;
    try {
      path = await ref
          .read(imageCaptureServiceProvider)
          .capture(source: ImageSource.gallery);
    } on Object catch (e) {
      _snack('Không mở được thư viện ảnh: $e');
      return;
    }
    if (!mounted || path == null) return;
    setState(() => _busy = true);
    await _process(path);
  }

  /// Shared: send [path] to OCR, then route to the review / failed screen.
  Future<void> _process(String path) async {
    try {
      final notifier = ref.read(scanControllerProvider.notifier);
      final job = _mode == CameraScanMode.label
          ? await notifier.scanLabel(path)
          : await notifier.scanReceipt(path);
      if (!mounted) return;
      if (job.isFailed || !job.hasItems) {
        context.push(
          '${Routes.pantry}/${Routes.scanFailed}',
          extra: _mode.scanType,
        );
        return;
      }
      final route = _mode == CameraScanMode.label
          ? Routes.scanLabelReview
          : Routes.scanReceiptReview;
      context.push('${Routes.pantry}/$route', extra: job);
    } on Object {
      if (mounted) {
        context.push(
          '${Routes.pantry}/${Routes.scanFailed}',
          extra: _mode.scanType,
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0D0B),
      body: Stack(
        fit: StackFit.expand,
        children: [
          if (_previewReady)
            _CoverPreview(controller: _controller!)
          else
            const ColoredBox(color: Color(0xFF0B0D0B)),
          // Slight scrim so the white chrome stays legible over the preview.
          const DecoratedBox(decoration: BoxDecoration(color: Colors.black26)),
          SafeArea(
            child: Column(
              children: [
                _Topbar(
                  mode: _mode,
                  torchOn: _torch,
                  torchEnabled: _previewReady,
                  onClose: () => context.pop(),
                  onToggleTorch: _toggleTorch,
                ),
                Expanded(
                  child: Center(
                    child: _Stage(
                      mode: _mode,
                      hint: _hint,
                      onGrant: _start,
                      onRetry: _start,
                      onGallery: _pickFromGallery,
                    ),
                  ),
                ),
                _ModeSwitcher(
                  mode: _mode,
                  onChanged: (m) => setState(() => _mode = m),
                ),
                Gap.gapMd,
                _ActionBar(
                  canShoot: _previewReady && !_busy,
                  onGallery: _pickFromGallery,
                  onShutter: _shoot,
                  onManual: () {
                    context.pop();
                    context.push('${Routes.pantry}/${Routes.addIngredient}');
                  },
                ),
              ],
            ),
          ),
          if (_busy)
            const Positioned.fill(
              child: ColoredBox(
                color: Colors.black54,
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      CircularProgressIndicator(color: Colors.white),
                      SizedBox(height: Gap.md),
                      Text(
                        'Đang đọc thông tin…',
                        style: TextStyle(color: Colors.white),
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// Full-bleed live preview, scaled to cover the screen (portrait-safe).
class _CoverPreview extends StatelessWidget {
  const _CoverPreview({required this.controller});

  final CameraController controller;

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);
    var scale = size.aspectRatio * controller.value.aspectRatio;
    if (scale < 1) scale = 1 / scale;
    return ClipRect(
      child: Transform.scale(
        scale: scale,
        alignment: Alignment.center,
        child: Center(child: CameraPreview(controller)),
      ),
    );
  }
}

/// The centre area: guide frame + status text / permission + retry affordances.
class _Stage extends StatelessWidget {
  const _Stage({
    required this.mode,
    required this.hint,
    required this.onGrant,
    required this.onRetry,
    required this.onGallery,
  });

  final CameraScanMode mode;
  final String? hint;
  final VoidCallback onGrant;
  final VoidCallback onRetry;
  final VoidCallback onGallery;

  @override
  Widget build(BuildContext context) {
    final white70 = Colors.white.withValues(alpha: 0.8);

    Widget caption(String text) => Text(
          text,
          textAlign: TextAlign.center,
          style: context.text.bodyMedium?.copyWith(color: white70),
        );

    if (hint == _CameraCaptureScreenState._kStarting) {
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ViewfinderOverlay(portrait: mode == CameraScanMode.receipt),
          Gap.gapLg,
          const SizedBox(
            width: 22,
            height: 22,
            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
          ),
          Gap.gapSm,
          caption('Đang mở máy ảnh…'),
        ],
      );
    }

    if (hint == null) {
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ViewfinderOverlay(portrait: mode == CameraScanMode.receipt),
          Gap.gapLg,
          caption(
            mode == CameraScanMode.label
                ? 'Đưa nhãn cân vào khung, giữ máy thẳng'
                : 'Đưa toàn bộ hóa đơn vào khung',
          ),
        ],
      );
    }

    // Error / permission state.
    final isPermission = hint == 'permission';
    return Padding(
      padding: const EdgeInsets.all(Gap.xl),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isPermission ? Icons.lock_outline_rounded : Icons.videocam_off_outlined,
            color: white70,
            size: 40,
          ),
          Gap.gapMd,
          caption(
            isPermission
                ? 'Cần quyền máy ảnh để quét trực tiếp.'
                : hint!,
          ),
          Gap.gapMd,
          Wrap(
            alignment: WrapAlignment.center,
            spacing: Gap.sm,
            runSpacing: Gap.xs,
            children: [
              FilledButton.icon(
                onPressed: isPermission ? onGrant : onRetry,
                icon: Icon(
                  isPermission
                      ? Icons.lock_open_rounded
                      : Icons.refresh_rounded,
                  size: 18,
                ),
                label: Text(isPermission ? 'Cấp quyền máy ảnh' : 'Thử lại'),
              ),
              OutlinedButton.icon(
                onPressed: onGallery,
                icon: const Icon(Icons.photo_library_outlined, size: 18),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: const BorderSide(color: Colors.white54),
                ),
                label: const Text('Dùng ảnh có sẵn'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Topbar extends StatelessWidget {
  const _Topbar({
    required this.mode,
    required this.torchOn,
    required this.torchEnabled,
    required this.onClose,
    required this.onToggleTorch,
  });

  final CameraScanMode mode;
  final bool torchOn;
  final bool torchEnabled;
  final VoidCallback onClose;
  final VoidCallback onToggleTorch;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: Gap.md, vertical: Gap.sm),
      child: Row(
        children: [
          IconButton(
            onPressed: onClose,
            style: IconButton.styleFrom(
              backgroundColor: Colors.white.withValues(alpha: 0.12),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            icon: const Icon(Icons.close_rounded, size: 20),
          ),
          const Spacer(),
          Text(
            'Quét ${mode.title.toLowerCase()}',
            style: context.text.titleMedium?.copyWith(
              color: Colors.white,
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          IconButton(
            onPressed: torchEnabled ? onToggleTorch : null,
            style: IconButton.styleFrom(
              backgroundColor: Colors.white.withValues(alpha: 0.12),
              foregroundColor: torchOn ? BrandPalette.green300 : Colors.white,
              disabledForegroundColor: Colors.white24,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            icon: Icon(
              torchOn ? Icons.flash_on_rounded : Icons.flash_off_rounded,
              size: 20,
            ),
          ),
        ],
      ),
    );
  }
}

class _ModeSwitcher extends StatelessWidget {
  const _ModeSwitcher({required this.mode, required this.onChanged});

  final CameraScanMode mode;
  final ValueChanged<CameraScanMode> onChanged;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: CameraScanMode.values.map((m) {
        final selected = m == mode;
        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: ChoiceChip(
            label: Text(m.title),
            selected: selected,
            showCheckmark: false,
            selectedColor: Colors.white,
            backgroundColor: Colors.black.withValues(alpha: 0.35),
            labelStyle: TextStyle(
              color: selected ? const Color(0xFF0B0D0B) : Colors.white70,
              fontWeight: FontWeight.w600,
              fontSize: 13,
            ),
            side: BorderSide.none,
            shape: const StadiumBorder(),
            onSelected: (_) => onChanged(m),
          ),
        );
      }).toList(),
    );
  }
}

class _ActionBar extends StatelessWidget {
  const _ActionBar({
    required this.canShoot,
    required this.onGallery,
    required this.onShutter,
    required this.onManual,
  });

  final bool canShoot;
  final VoidCallback onGallery;
  final VoidCallback onShutter;
  final VoidCallback onManual;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(Gap.xl, 0, Gap.xl, Gap.xl),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            onPressed: onGallery,
            iconSize: 22,
            style: IconButton.styleFrom(
              fixedSize: const Size(44, 44),
              backgroundColor: Colors.white.withValues(alpha: 0.15),
              foregroundColor: Colors.white.withValues(alpha: 0.8),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            icon: const Icon(Icons.photo_library_outlined),
          ),
          GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: canShoot ? onShutter : null,
            child: Opacity(
              opacity: canShoot ? 1 : 0.4,
              child: Container(
                width: 70,
                height: 70,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white,
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.35),
                    width: 5,
                  ),
                ),
              ),
            ),
          ),
          GestureDetector(
            onTap: onManual,
            child: SizedBox(
              width: 60,
              child: Text(
                'Nhập tay',
                textAlign: TextAlign.center,
                style: context.text.labelLarge?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
