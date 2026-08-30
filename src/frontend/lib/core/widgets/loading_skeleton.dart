import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';

/// A single shimmering placeholder block.
class SkeletonBox extends StatefulWidget {
  const SkeletonBox({
    this.width,
    this.height = 14,
    this.radius = Radii.sm,
    super.key,
  });

  final double? width;
  final double height;
  final double radius;

  @override
  State<SkeletonBox> createState() => _SkeletonBoxState();
}

class _SkeletonBoxState extends State<SkeletonBox>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1200),
  )..repeat();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final base = context.sweep.subtleFill;
    final hi = Color.alphaBlend(
      context.colors.surface.withValues(alpha: 0.6),
      base,
    );
    return AnimatedBuilder(
      animation: _c,
      builder: (context, _) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(widget.radius),
            gradient: LinearGradient(
              begin: Alignment(-1 - 2 * _c.value, 0),
              end: Alignment(1 - 2 * _c.value, 0),
              colors: [base, hi, base],
              stops: const [0.35, 0.5, 0.65],
            ),
          ),
        );
      },
    );
  }
}

/// A list of skeleton "cards" for loading list screens.
class SkeletonList extends StatelessWidget {
  const SkeletonList({this.count = 5, super.key});
  final int count;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(Gap.lg),
      itemCount: count,
      separatorBuilder: (_, __) => const SizedBox(height: Gap.sm),
      itemBuilder: (_, __) => Container(
        padding: const EdgeInsets.all(Gap.sm),
        decoration: BoxDecoration(
          borderRadius: Radii.brLg,
          border: Border.all(color: context.sweep.hairline),
        ),
        child: const Row(
          children: [
            SkeletonBox(width: 44, height: 44, radius: Radii.md),
            SizedBox(width: Gap.sm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SkeletonBox(width: 160),
                  SizedBox(height: Gap.xs),
                  SkeletonBox(width: 96, height: 10),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
