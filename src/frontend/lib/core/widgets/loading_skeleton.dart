import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// A single shimmering placeholder block.
///
/// Honors `MediaQuery.disableAnimationsOf(context)` by rendering a calm static
/// surface fill instead of a sweeping shimmer.
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
  AnimationController? _c;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final disable = MediaQuery.disableAnimationsOf(context);
    if (disable) {
      _c?.dispose();
      _c = null;
    } else {
      _c ??= AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 1200),
      )..repeat();
    }
  }

  @override
  void dispose() {
    _c?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final base = context.sweep.subtleFill;
    final ctrl = _c;
    if (ctrl == null) {
      return Container(
        width: widget.width,
        height: widget.height,
        decoration: BoxDecoration(
          color: base,
          borderRadius: BorderRadius.circular(widget.radius),
        ),
      );
    }

    final hi = Color.alphaBlend(
      context.colors.surface.withValues(alpha: 0.65),
      base,
    );
    return AnimatedBuilder(
      animation: ctrl,
      builder: (context, _) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(widget.radius),
            gradient: LinearGradient(
              begin: Alignment(-1 - 2 * ctrl.value, 0),
              end: Alignment(1 - 2 * ctrl.value, 0),
              colors: [base, hi, base],
              stops: const [0.35, 0.5, 0.65],
            ),
          ),
        );
      },
    );
  }
}

/// Suppresses skeleton flash for fast (<180ms) loads (`ui-states-and-feedback`).
class DelayedSkeleton extends StatefulWidget {
  const DelayedSkeleton({
    required this.child,
    this.delay = const Duration(milliseconds: 180),
    super.key,
  });

  final Widget child;
  final Duration delay;

  @override
  State<DelayedSkeleton> createState() => _DelayedSkeletonState();
}

class _DelayedSkeletonState extends State<DelayedSkeleton> {
  bool _visible = false;

  @override
  void initState() {
    super.initState();
    Future<void>.delayed(widget.delay, () {
      if (mounted) setState(() => _visible = true);
    });
  }

  @override
  Widget build(BuildContext context) =>
      _visible ? widget.child : const SizedBox.shrink();
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
          color: context.colors.surfaceContainerLowest,
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
            SizedBox(width: Gap.sm),
            SkeletonBox(width: 68, height: 22, radius: Radii.pill),
          ],
        ),
      ),
    );
  }
}

/// Layout-matched skeleton for Home dashboard.
class HomeDashboardSkeleton extends StatelessWidget {
  const HomeDashboardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xxl),
      children: const [
        SkeletonBox(width: 110, height: 13),
        SizedBox(height: 6),
        SkeletonBox(width: 210, height: 28, radius: Radii.sm),
        SizedBox(height: Gap.md),
        SkeletonBox(height: 112, radius: Radii.lg),
        SizedBox(height: Gap.lg),
        SkeletonBox(width: 130, height: 12),
        SizedBox(height: Gap.sm),
        Row(
          children: [
            Expanded(child: SkeletonBox(height: 128, radius: 16)),
            SizedBox(width: Gap.sm),
            Expanded(child: SkeletonBox(height: 128, radius: 16)),
          ],
        ),
        SizedBox(height: Gap.lg),
        SkeletonBox(height: 220, radius: 16),
      ],
    );
  }
}

/// Layout-matched skeleton for suggestion card lists.
class SuggestionSkeleton extends StatelessWidget {
  const SuggestionSkeleton({this.count = 3, super.key});
  final int count;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.sm, Gap.lg, Gap.xxl),
      itemCount: count,
      separatorBuilder: (_, __) => const SizedBox(height: Gap.md),
      itemBuilder: (_, __) => Container(
        decoration: BoxDecoration(
          color: context.colors.surfaceContainerLowest,
          borderRadius: Radii.brLg,
          border: Border.all(color: context.sweep.hairline),
        ),
        clipBehavior: Clip.antiAlias,
        child: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SkeletonBox(height: 156, radius: 0),
            Padding(
              padding: EdgeInsets.all(Gap.md),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SkeletonBox(width: 185, height: 18),
                  SizedBox(height: Gap.xs),
                  SkeletonBox(width: 140, height: 12),
                  SizedBox(height: Gap.sm),
                  Row(
                    children: [
                      SkeletonBox(width: 92, height: 24, radius: Radii.pill),
                      SizedBox(width: Gap.xs),
                      SkeletonBox(width: 78, height: 24, radius: Radii.pill),
                    ],
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
