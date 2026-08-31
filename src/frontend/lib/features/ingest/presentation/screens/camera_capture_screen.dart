// lib/features/ingest/presentation/screens/camera_capture_screen.dart
// I-01 Quét tem nhãn & I-04 Quét hóa đơn
// Design: CameraCapture.dc.html

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/media/image_capture_service.dart';
import 'package:frontend/core/media/media_providers.dart';
import 'package:frontend/core/permissions/permission_prime_sheet.dart';
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

/// I-01 / I-04 — chụp ảnh tem nhãn / hóa đơn, gửi OCR, rồi mở màn kiểm tra.
class CameraCaptureScreen extends ConsumerStatefulWidget {
  const CameraCaptureScreen({this.initialMode = CameraScanMode.label, super.key});

  final CameraScanMode initialMode;

  @override
  ConsumerState<CameraCaptureScreen> createState() =>
      _CameraCaptureScreenState();
}

class _CameraCaptureScreenState extends ConsumerState<CameraCaptureScreen> {
  late CameraScanMode _mode = widget.initialMode;
  bool _flashOn = false;
  bool _busy = false;

  Future<void> _capture(ImageSource source) async {
    if (_busy) return;

    if (source == ImageSource.camera) {
      final ok = await ensureMediaPermission(
        context,
        ref,
        PermissionKind.camera,
      );
      if (!ok || !mounted) return;
    }

    String? path;
    try {
      // Crop (I-02) is deferred to M6 — needs a UCropActivity in the Android
      // manifest. Camera / gallery → straight to the review screen for now.
      path = await ref
          .read(imageCaptureServiceProvider)
          .capture(source: source);
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              source == ImageSource.camera
                  ? 'Không mở được máy ảnh: $e'
                  : 'Không mở được thư viện ảnh: $e',
            ),
          ),
        );
      }
      return;
    }
    if (!mounted || path == null) return;

    setState(() => _busy = true);
    try {
      final notifier = ref.read(scanControllerProvider.notifier);
      final job = _mode == CameraScanMode.label
          ? await notifier.scanLabel(path)
          : await notifier.scanReceipt(path);
      if (!mounted) return;
      if (job.isFailed || !job.hasItems) {
        context.push('${Routes.pantry}/${Routes.scanFailed}', extra: _mode.scanType);
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
      body: SafeArea(
        child: Stack(
          children: [
            Column(
              children: [
                _Topbar(
                  mode: _mode,
                  flashOn: _flashOn,
                  onClose: () => context.pop(),
                  onToggleFlash: () => setState(() => _flashOn = !_flashOn),
                ),
                Expanded(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      ViewfinderOverlay(
                        portrait: _mode == CameraScanMode.receipt,
                      ),
                      Gap.gapLg,
                      Text(
                        _mode == CameraScanMode.label
                            ? 'Đưa nhãn cân vào khung, giữ máy thẳng'
                            : 'Đưa toàn bộ hóa đơn vào khung',
                        style: context.text.bodyMedium?.copyWith(
                          color: Colors.white.withValues(alpha: 0.8),
                        ),
                      ),
                    ],
                  ),
                ),
                _ModeSwitcher(
                  mode: _mode,
                  onChanged: (m) => setState(() => _mode = m),
                ),
                Gap.gapMd,
                _ActionBar(
                  onGallery: () => _capture(ImageSource.gallery),
                  onShutter: () => _capture(ImageSource.camera),
                  onManual: () {
                    context.pop();
                    context.push('${Routes.pantry}/${Routes.addIngredient}');
                  },
                ),
              ],
            ),
            if (_busy)
              const ColoredBox(
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
          ],
        ),
      ),
    );
  }
}

class _Topbar extends StatelessWidget {
  const _Topbar({
    required this.mode,
    required this.flashOn,
    required this.onClose,
    required this.onToggleFlash,
  });

  final CameraScanMode mode;
  final bool flashOn;
  final VoidCallback onClose;
  final VoidCallback onToggleFlash;

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
            onPressed: onToggleFlash,
            style: IconButton.styleFrom(
              backgroundColor: Colors.white.withValues(alpha: 0.12),
              foregroundColor:
                  flashOn ? BrandPalette.green300 : Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            icon: Icon(
              flashOn ? Icons.flash_on_rounded : Icons.flash_off_rounded,
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
            backgroundColor: Colors.transparent,
            labelStyle: TextStyle(
              color: selected ? const Color(0xFF0B0D0B) : Colors.white54,
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
    required this.onGallery,
    required this.onShutter,
    required this.onManual,
  });

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
            onTap: onShutter,
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
