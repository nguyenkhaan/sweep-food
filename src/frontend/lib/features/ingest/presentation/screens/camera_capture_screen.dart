// lib/features/ingest/presentation/screens/camera_capture_screen.dart
// I-01 Quét tem nhãn & I-04 Quét hóa đơn
// Design: CameraCapture.dc.html

import 'dart:async';
import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/media/image_capture_service.dart';
import 'package:sweepfood/core/media/media_providers.dart';
import 'package:sweepfood/core/permissions/permission_prime_sheet.dart';
import 'package:sweepfood/core/permissions/permission_service.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/logger.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/scan_controller.dart';
import 'package:sweepfood/features/ingest/presentation/widgets/viewfinder_overlay.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

enum CameraScanMode {
  label(ScanType.label),
  receipt(ScanType.receipt);

  const CameraScanMode(this.scanType);

  final ScanType scanType;

  String title(AppL10n l10n) => switch (this) {
    CameraScanMode.label => l10n.camModeLabel,
    CameraScanMode.receipt => l10n.camModeReceipt,
  };
}

/// I-01 / I-04 — khung ngắm camera trực tiếp trong app; nút trắng chụp lại
/// khung hình hiện tại rồi gửi OCR (không mở app máy ảnh của hệ thống).
class CameraCaptureScreen extends ConsumerStatefulWidget {
  const CameraCaptureScreen({
    this.initialMode = CameraScanMode.label,
    super.key,
  });

  final CameraScanMode initialMode;

  @override
  ConsumerState<CameraCaptureScreen> createState() =>
      _CameraCaptureScreenState();
}

class _CameraCaptureScreenState extends ConsumerState<CameraCaptureScreen>
    with WidgetsBindingObserver, SingleTickerProviderStateMixin {
  late CameraScanMode _mode = widget.initialMode;
  CameraController? _controller;
  bool _torch = false;
  bool _busy = false;

  /// True only while waiting for `takePicture()` (shutter shows a spinner).
  bool _shooting = false;

  /// The photo being processed; shown full-bleed instead of the live preview
  /// so the user sees exactly what was captured. `null` = preview is live.
  String? _capturedPath;
  bool _capturedFromCamera = false;

  /// Short white shutter flash: jumps to 1 on tap, fades back to 0.
  late final AnimationController _flash = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 150),
  );

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
    _flash.dispose();
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
        if (mounted) setState(() => _hint = context.l10n.camNoCamera);
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
        // A fresh controller is live; never keep a stale frozen frame over it
        // (an in-flight scan clears its own frame when it finishes).
        if (!_busy) _capturedPath = null;
      });
    } on Object catch (e) {
      if (mounted) setState(() => _hint = context.l10n.camOpenError('$e'));
    }
  }

  void _snack(String msg) {
    if (!mounted) return;
    AppSnack.show(context, msg);
  }

  Future<void> _toggleTorch() async {
    final c = _controller;
    if (c == null || !c.value.isInitialized) return;
    final l10n = context.l10n;
    try {
      await c.setFlashMode(_torch ? FlashMode.off : FlashMode.torch);
      if (mounted) setState(() => _torch = !_torch);
    } on Object {
      _snack(l10n.camNoFlash);
    }
  }

  Future<void> _shoot() async {
    final c = _controller;
    if (_busy ||
        c == null ||
        !c.value.isInitialized ||
        c.value.isTakingPicture) {
      return;
    }
    final l10n = context.l10n;
    // Instant feedback before the (slow) capture returns.
    unawaited(HapticFeedback.mediumImpact());
    _flash.value = 1;
    unawaited(_flash.reverse());
    setState(() {
      _busy = true;
      _shooting = true;
    });
    final XFile shot;
    try {
      shot = await c.takePicture();
    } on Object catch (e) {
      if (mounted) {
        setState(() {
          _busy = false;
          _shooting = false;
          _capturedPath = null;
        });
        _snack(l10n.camShootError('$e'));
      }
      await _resumePreview();
      return;
    }
    if (!mounted) return;
    await _process(shot.path, fromCamera: true);
  }

  Future<void> _pickFromGallery() async {
    if (_busy) return;
    final l10n = context.l10n;
    String? path;
    try {
      path = await ref
          .read(imageCaptureServiceProvider)
          .capture(source: ImageSource.gallery);
    } on Object catch (e) {
      _snack(l10n.camGalleryError('$e'));
      return;
    }
    if (!mounted || path == null || _busy) return;
    await _process(path);
  }

  /// Freezes the screen on [path]: torch off, live preview paused.
  Future<void> _freeze(String path, {required bool fromCamera}) async {
    setState(() {
      _busy = true;
      _shooting = false;
      _capturedPath = path;
      _capturedFromCamera = fromCamera;
    });
    final c = _controller;
    if (c == null || !c.value.isInitialized) return;
    if (_torch) {
      try {
        await c.setFlashMode(FlashMode.off);
      } on Object catch (e) {
        log.w('Could not turn the torch off', error: e);
      }
      if (mounted) setState(() => _torch = false);
    }
    try {
      await c.pausePreview();
    } on Object catch (e) {
      // Not supported everywhere; the frozen image covers the preview anyway.
      log.w('pausePreview failed', error: e);
    }
  }

  Future<void> _resumePreview() async {
    final c = _controller;
    if (c == null || !c.value.isInitialized || !c.value.isPreviewPaused) {
      return;
    }
    try {
      await c.resumePreview();
    } on Object catch (e) {
      log.w('resumePreview failed', error: e);
    }
  }

  /// Sends [path] to OCR, then routes to the review or failed screen.
  Future<void> _process(String path, {bool fromCamera = false}) async {
    // Pin the mode for the whole flow; the switcher is locked while busy, but
    // never let a late change route a label photo down the receipt branch.
    final mode = _mode;
    try {
      await _freeze(path, fromCamera: fromCamera);
      final notifier = ref.read(scanControllerProvider.notifier);
      final ScanJob job;
      if (mode == CameraScanMode.label) {
        job = await notifier.scanLabel(path);
      } else {
        job = await notifier.scanReceipt(path);
      }
      if (!mounted) return;
      log.d(
        'Scan result type=${job.type.wire} status=${job.status.wire} '
        'items=${job.items.length} hasRawText=${job.rawText?.trim().isNotEmpty == true}',
      );
      // A receipt can be a valid PARTIAL result even when OCR read text but
      // could not turn it into line items. Route that outcome to the review
      // screen so the user can inspect it, retake, or enter items manually.
      final hasUsableResult =
          job.hasItems || (mode == CameraScanMode.receipt && !job.isFailed);
      if (job.isFailed || !hasUsableResult) {
        context.push(
          '${Routes.pantry}/${Routes.scanFailed}',
          extra: mode.scanType,
        );
        return;
      }
      final route = mode == CameraScanMode.receipt
          ? Routes.scanReceiptReview
          : Routes.scanLabelReview;
      context.push('${Routes.pantry}/$route', extra: job);
    } on Object catch (error, stackTrace) {
      log.w(
        'Scan flow failed before review',
        error: error,
        stackTrace: stackTrace,
      );
      if (mounted) {
        context.push(
          '${Routes.pantry}/${Routes.scanFailed}',
          extra: mode.scanType,
        );
      }
    } finally {
      // `context.push` is not awaited: reset now so the camera is live again
      // when the user pops back from review / scanFailed.
      if (mounted) {
        setState(() {
          _busy = false;
          _shooting = false;
          _capturedPath = null;
        });
        await _resumePreview();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0D0B),
      body: Stack(
        fit: StackFit.expand,
        children: [
          if (_capturedPath != null)
            _CapturedImage(path: _capturedPath!)
          else if (_previewReady)
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
                  torchEnabled: _previewReady && !_busy,
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
                  enabled: !_busy,
                  onChanged: (m) => setState(() => _mode = m),
                ),
                Gap.gapMd,
                _ActionBar(
                  enabled: !_busy,
                  canShoot: _previewReady && !_busy,
                  shooting: _shooting,
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
          if (_capturedPath != null)
            Positioned.fill(
              child: _ProcessingOverlay(captured: _capturedFromCamera),
            ),
          Positioned.fill(
            child: IgnorePointer(
              child: FadeTransition(
                opacity: _flash,
                child: const ColoredBox(color: Colors.white),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// The captured / picked photo, full-bleed like [_CoverPreview].
class _CapturedImage extends StatelessWidget {
  const _CapturedImage({required this.path});

  final String path;

  @override
  Widget build(BuildContext context) {
    const fallback = ColoredBox(color: Color(0xFF0B0D0B));
    // On web, camera / image_picker hand back blob URLs rather than files.
    return kIsWeb
        ? Image.network(
            path,
            fit: BoxFit.cover,
            gaplessPlayback: true,
            errorBuilder: (_, __, ___) => fallback,
          )
        : Image.file(
            File(path),
            fit: BoxFit.cover,
            gaplessPlayback: true,
            errorBuilder: (_, __, ___) => fallback,
          );
  }
}

/// Scrim + spinner over the frozen photo while it is uploaded / read.
class _ProcessingOverlay extends StatelessWidget {
  const _ProcessingOverlay({required this.captured});

  /// Shows the "photo captured" confirmation line (camera shots only).
  final bool captured;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return ColoredBox(
      color: Colors.black45,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (captured) ...[
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(
                    Icons.check_circle_rounded,
                    color: BrandPalette.green300,
                    size: 20,
                  ),
                  const SizedBox(width: Gap.xs),
                  Text(
                    l10n.camCaptured,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: Gap.md),
            ],
            const CircularProgressIndicator(color: Colors.white),
            const SizedBox(height: Gap.md),
            Text(l10n.camReading, style: const TextStyle(color: Colors.white)),
          ],
        ),
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
    final l10n = context.l10n;
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
            child: CircularProgressIndicator(
              color: Colors.white,
              strokeWidth: 2,
            ),
          ),
          Gap.gapSm,
          caption(l10n.camOpening),
        ],
      );
    }

    if (hint == null) {
      final String guide;
      switch (mode) {
        case CameraScanMode.label:
          guide = l10n.camGuideLabel;
          break;
        case CameraScanMode.receipt:
          guide = l10n.camGuideReceipt;
          break;
      }
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ViewfinderOverlay(portrait: mode == CameraScanMode.receipt),
          Gap.gapLg,
          caption(guide),
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
            isPermission
                ? Icons.lock_outline_rounded
                : Icons.videocam_off_outlined,
            color: white70,
            size: 40,
          ),
          Gap.gapMd,
          caption(isPermission ? l10n.camPermissionNeeded : hint!),
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
                label: Text(
                  isPermission ? l10n.camGrantPermission : l10n.commonRetry,
                ),
              ),
              OutlinedButton.icon(
                onPressed: onGallery,
                icon: const Icon(Icons.photo_library_outlined, size: 18),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: const BorderSide(color: Colors.white54),
                ),
                label: Text(l10n.camUseGallery),
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
            context.l10n.camScanTitle(mode.title(context.l10n).toLowerCase()),
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
  const _ModeSwitcher({
    required this.mode,
    required this.enabled,
    required this.onChanged,
  });

  final CameraScanMode mode;
  final bool enabled;
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
            label: Text(m.title(context.l10n)),
            selected: selected,
            showCheckmark: false,
            selectedColor: Colors.white,
            backgroundColor: Colors.black.withValues(alpha: 0.35),
            disabledColor: selected
                ? Colors.white54
                : Colors.black.withValues(alpha: 0.2),
            labelStyle: TextStyle(
              color: selected ? const Color(0xFF0B0D0B) : Colors.white70,
              fontWeight: FontWeight.w600,
              fontSize: 13,
            ),
            side: BorderSide.none,
            shape: const StadiumBorder(),
            onSelected: enabled ? (_) => onChanged(m) : null,
          ),
        );
      }).toList(),
    );
  }
}

class _ActionBar extends StatelessWidget {
  const _ActionBar({
    required this.enabled,
    required this.canShoot,
    required this.shooting,
    required this.onGallery,
    required this.onShutter,
    required this.onManual,
  });

  /// Gallery + manual entry; off while a scan is in flight.
  final bool enabled;
  final bool canShoot;

  /// Waiting for the camera to return the photo.
  final bool shooting;
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
            onPressed: enabled ? onGallery : null,
            iconSize: 22,
            style: IconButton.styleFrom(
              fixedSize: const Size(44, 44),
              backgroundColor: Colors.white.withValues(alpha: 0.15),
              foregroundColor: Colors.white.withValues(alpha: 0.8),
              disabledBackgroundColor: Colors.white.withValues(alpha: 0.08),
              disabledForegroundColor: Colors.white24,
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
              opacity: canShoot || shooting ? 1 : 0.4,
              child: Container(
                width: 70,
                height: 70,
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white,
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.35),
                    width: 5,
                  ),
                ),
                child: shooting
                    ? const CircularProgressIndicator(
                        color: Color(0xFF0B0D0B),
                        strokeWidth: 2.5,
                      )
                    : null,
              ),
            ),
          ),
          GestureDetector(
            onTap: enabled ? onManual : null,
            child: Opacity(
              opacity: enabled ? 1 : 0.4,
              child: SizedBox(
                width: 60,
                child: Text(
                  context.l10n.chooserManual,
                  textAlign: TextAlign.center,
                  style: context.text.labelLarge?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
