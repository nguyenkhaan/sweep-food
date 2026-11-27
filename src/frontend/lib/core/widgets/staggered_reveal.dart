import 'package:flutter/material.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Subtle one-shot fade + lift entrance for cards and sections.
///
/// Automatically disables motion when `MediaQuery.disableAnimationsOf` is true.
class StaggeredReveal extends StatefulWidget {
  const StaggeredReveal({
    required this.child,
    this.index = 0,
    this.stepDelayMs = 45,
    super.key,
  });

  final Widget child;
  final int index;
  final int stepDelayMs;

  @override
  State<StaggeredReveal> createState() => _StaggeredRevealState();
}

class _StaggeredRevealState extends State<StaggeredReveal>
    with SingleTickerProviderStateMixin {
  AnimationController? _ctrl;
  Animation<double>? _opacity;
  Animation<Offset>? _offset;
  bool _started = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_started) return;
    _started = true;

    if (MediaQuery.disableAnimationsOf(context)) return;

    final delay = (widget.index.clamp(0, 6)) * widget.stepDelayMs;
    final total = context.motion.medium + Duration(milliseconds: delay);
    final ctrl = AnimationController(vsync: this, duration: total);
    _ctrl = ctrl;

    final startFrac = total.inMilliseconds == 0
        ? 0.0
        : (delay / total.inMilliseconds).clamp(0.0, 0.65);
    final curved = CurvedAnimation(
      parent: ctrl,
      curve: Interval(startFrac, 1.0, curve: context.motion.enterCurve),
    );
    _opacity = curved;
    _offset = Tween<Offset>(
      begin: const Offset(0, 0.045),
      end: Offset.zero,
    ).animate(curved);

    ctrl.forward();
  }

  @override
  void dispose() {
    _ctrl?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_ctrl == null || _opacity == null || _offset == null) {
      return widget.child;
    }
    return FadeTransition(
      opacity: _opacity!,
      child: SlideTransition(position: _offset!, child: widget.child),
    );
  }
}
