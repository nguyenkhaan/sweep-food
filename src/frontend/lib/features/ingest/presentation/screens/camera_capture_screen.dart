// lib/features/ingest/presentation/screens/camera_capture_screen.dart
// I-01 Quét tem nhãn & I-04 Quét hóa đơn
// Design: CameraCapture.dc.html

import 'package:flutter/material.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';

enum CameraScanMode {
  label('Tem nhãn'),
  receipt('Hóa đơn');

  const CameraScanMode(this.title);
  final String title;
}

/// I-01 / I-04 — Màn hình chụp ảnh tem nhãn / hóa đơn.
class CameraCaptureScreen extends StatefulWidget {
  const CameraCaptureScreen({
    this.initialMode = CameraScanMode.label,
    super.key,
  });

  final CameraScanMode initialMode;

  @override
  State<CameraCaptureScreen> createState() => _CameraCaptureScreenState();
}

class _CameraCaptureScreenState extends State<CameraCaptureScreen> {
  late CameraScanMode _mode;
  bool _flashOn = false;
  final ImagePicker _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _mode = widget.initialMode;
  }

  Future<void> _captureImage(ImageSource source) async {
    try {
      final image = await _picker.pickImage(source: source);
      if (!mounted || image == null) return;

      // Navigate to review screen based on current mode
      if (_mode == CameraScanMode.label) {
        context.push('${Routes.pantry}/scan/label-review', extra: image.path);
      } else {
        context.push('${Routes.pantry}/scan/receipt-review', extra: image.path);
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Không thể chụp ảnh: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0D0B),
      body: SafeArea(
        child: Column(
          children: [
            // ── Topbar ────────────────────────────────────────────────────────
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: Gap.md,
                vertical: Gap.sm,
              ),
              child: Row(
                children: [
                  IconButton(
                    onPressed: () => context.pop(),
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
                    'Quét ${_mode.title.toLowerCase()}',
                    style: context.text.titleMedium?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const Spacer(),
                  IconButton(
                    onPressed: () => setState(() => _flashOn = !_flashOn),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.white.withValues(alpha: 0.12),
                      foregroundColor:
                          _flashOn ? BrandPalette.green300 : Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    icon: Icon(
                      _flashOn ? Icons.flash_on_rounded : Icons.flash_off_rounded,
                      size: 20,
                    ),
                  ),
                ],
              ),
            ),

            // ── Viewfinder Overlay Frame ─────────────────────────────────────
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _ViewfinderGuide(mode: _mode),
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

            // ── Mode Switcher ────────────────────────────────────────────────
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: CameraScanMode.values.map((m) {
                final selected = m == _mode;
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
                    onSelected: (_) => setState(() => _mode = m),
                  ),
                );
              }).toList(),
            ),
            Gap.gapMd,

            // ── Bottom Action Bar ────────────────────────────────────────────
            Padding(
              padding: const EdgeInsets.fromLTRB(Gap.xl, 0, Gap.xl, Gap.xl),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Gallery button
                  IconButton(
                    onPressed: () => _captureImage(ImageSource.gallery),
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

                  // Shutter button
                  GestureDetector(
                    onTap: () => _captureImage(ImageSource.camera),
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

                  // Manual entry button
                  GestureDetector(
                    onTap: () {
                      context.pop();
                      context.push('${Routes.pantry}/${Routes.addIngredient}');
                    },
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
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Viewfinder Guide Widget
// ─────────────────────────────────────────────────────────────────────────────

class _ViewfinderGuide extends StatelessWidget {
  const _ViewfinderGuide({required this.mode});

  final CameraScanMode mode;

  @override
  Widget build(BuildContext context) {
    final isLabel = mode == CameraScanMode.label;
    final width = isLabel ? 260.0 : 280.0;
    final height = isLabel ? 180.0 : 340.0;

    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
      ),
      child: const CustomPaint(
        painter: _CornerGuidePainter(color: BrandPalette.green300),
      ),
    );
  }
}

class _CornerGuidePainter extends CustomPainter {
  const _CornerGuidePainter({required this.color});

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;

    const cornerLength = 26.0;
    const radius = 8.0;

    // Top Left
    final pathTL = Path()
      ..moveTo(0, cornerLength)
      ..lineTo(0, radius)
      ..quadraticBezierTo(0, 0, radius, 0)
      ..lineTo(cornerLength, 0);
    canvas.drawPath(pathTL, paint);

    // Top Right
    final pathTR = Path()
      ..moveTo(size.width - cornerLength, 0)
      ..lineTo(size.width - radius, 0)
      ..quadraticBezierTo(size.width, 0, size.width, radius)
      ..lineTo(size.width, cornerLength);
    canvas.drawPath(pathTR, paint);

    // Bottom Left
    final pathBL = Path()
      ..moveTo(0, size.height - cornerLength)
      ..lineTo(0, size.height - radius)
      ..quadraticBezierTo(0, size.height, radius, size.height)
      ..lineTo(cornerLength, size.height);
    canvas.drawPath(pathBL, paint);

    // Bottom Right
    final pathBR = Path()
      ..moveTo(size.width - cornerLength, size.height)
      ..lineTo(size.width - radius, size.height)
      ..quadraticBezierTo(size.width, size.height, size.width, size.height - radius)
      ..lineTo(size.width, size.height - cornerLength);
    canvas.drawPath(pathBR, paint);
  }

  @override
  bool shouldRepaint(covariant _CornerGuidePainter oldDelegate) =>
      color != oldDelegate.color;
}
