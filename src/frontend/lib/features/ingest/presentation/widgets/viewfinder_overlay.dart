// lib/features/ingest/presentation/widgets/viewfinder_overlay.dart
// Camera frame guide overlay (I-01 / I-04)

import 'package:flutter/material.dart';

/// Rounded corner-bracket guide with a gentle scanning beam drawn over the
/// camera preview. [portrait] uses a tall frame for receipts; labels use wide.
class ViewfinderOverlay extends StatefulWidget {
  const ViewfinderOverlay({this.portrait = false, this.color, super.key});

  final bool portrait;
  final Color? color;

  @override
  State<ViewfinderOverlay> createState() => _ViewfinderOverlayState();
}

class _ViewfinderOverlayState extends State<ViewfinderOverlay>
    with SingleTickerProviderStateMixin {
  AnimationController? _beamController;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final disableMotion = MediaQuery.disableAnimationsOf(context);
    if (disableMotion) {
      _beamController?.stop();
      _beamController?.dispose();
      _beamController = null;
    } else {
      _beamController ??= AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 1800),
      )..repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _beamController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final w = widget.portrait ? 280.0 : 260.0;
    final h = widget.portrait ? 340.0 : 180.0;
    final accent =
        widget.color ?? Theme.of(context).colorScheme.primaryContainer;

    return SizedBox(
      width: w,
      height: h,
      child: Stack(
        alignment: Alignment.center,
        children: [
          CustomPaint(
            size: Size(w, h),
            painter: _CornerGuidePainter(color: accent),
          ),
          if (_beamController != null)
            AnimatedBuilder(
              animation: _beamController!,
              builder: (_, __) {
                final y = 16 + _beamController!.value * (h - 32);
                return Positioned(
                  left: 14,
                  right: 14,
                  top: y,
                  child: Container(
                    height: 2,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          accent.withValues(alpha: 0),
                          accent.withValues(alpha: 0.9),
                          accent.withValues(alpha: 0),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
        ],
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
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

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
