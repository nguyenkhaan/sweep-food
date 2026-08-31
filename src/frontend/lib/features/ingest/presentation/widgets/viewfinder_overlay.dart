// lib/features/ingest/presentation/widgets/viewfinder_overlay.dart
// Camera frame guide overlay (I-01 / I-04)

import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_colors.dart';

/// Rounded corner-bracket guide drawn over the camera preview. [portrait] uses
/// a tall frame (receipts); otherwise a wide frame (weight labels).
class ViewfinderOverlay extends StatelessWidget {
  const ViewfinderOverlay({
    this.portrait = false,
    this.color = BrandPalette.green300,
    super.key,
  });

  final bool portrait;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: portrait ? 280 : 260,
      height: portrait ? 340 : 180,
      child: CustomPaint(
        painter: _CornerGuidePainter(color: color),
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
    final w = size.width;
    final h = size.height;

    final tl = Path()
      ..moveTo(0, cornerLength)
      ..lineTo(0, radius)
      ..quadraticBezierTo(0, 0, radius, 0)
      ..lineTo(cornerLength, 0);
    final tr = Path()
      ..moveTo(w - cornerLength, 0)
      ..lineTo(w - radius, 0)
      ..quadraticBezierTo(w, 0, w, radius)
      ..lineTo(w, cornerLength);
    final bl = Path()
      ..moveTo(0, h - cornerLength)
      ..lineTo(0, h - radius)
      ..quadraticBezierTo(0, h, radius, h)
      ..lineTo(cornerLength, h);
    final br = Path()
      ..moveTo(w - cornerLength, h)
      ..lineTo(w - radius, h)
      ..quadraticBezierTo(w, h, w, h - radius)
      ..lineTo(w, h - cornerLength);

    for (final p in [tl, tr, bl, br]) {
      canvas.drawPath(p, paint);
    }
  }

  @override
  bool shouldRepaint(covariant _CornerGuidePainter old) => old.color != color;
}
