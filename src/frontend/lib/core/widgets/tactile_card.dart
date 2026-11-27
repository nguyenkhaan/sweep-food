import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// A press-responsive card surface with subtle tactile scale-down + haptic click.
///
/// Collapses scale animation to zero under `MediaQuery.disableAnimationsOf`.
class TactileCard extends StatefulWidget {
  const TactileCard({
    required this.child,
    this.onTap,
    this.onLongPress,
    this.color,
    this.borderColor,
    this.borderWidth = 1,
    this.borderRadius = Radii.brLg,
    this.boxShadow,
    this.padding,
    this.semanticLabel,
    this.haptic = true,
    super.key,
  });

  final Widget child;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final Color? color;
  final Color? borderColor;
  final double borderWidth;
  final BorderRadius borderRadius;
  final List<BoxShadow>? boxShadow;
  final EdgeInsetsGeometry? padding;
  final String? semanticLabel;
  final bool haptic;

  @override
  State<TactileCard> createState() => _TactileCardState();
}

class _TactileCardState extends State<TactileCard> {
  bool _pressed = false;

  void _setPressed(bool next) {
    if (_pressed == next || widget.onTap == null) return;
    setState(() => _pressed = next);
  }

  @override
  Widget build(BuildContext context) {
    final motion = context.motion;
    final duration = AppMotion.resolve(context, motion.fast);
    final curve = AppMotion.resolveCurve(context, motion.enterCurve);
    final bg = widget.color ?? context.colors.surfaceContainerLowest;
    final border = widget.borderColor ?? context.sweep.hairline;

    final card = AnimatedScale(
      scale: _pressed ? 0.978 : 1.0,
      duration: duration,
      curve: curve,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: bg,
          borderRadius: widget.borderRadius,
          boxShadow: widget.boxShadow,
        ),
        child: Material(
          color: Colors.transparent,
          borderRadius: widget.borderRadius,
          clipBehavior: Clip.antiAlias,
          child: InkWell(
            onTap: widget.onTap == null
                ? null
                : () {
                    if (widget.haptic) AppHaptics.selection();
                    widget.onTap!();
                  },
            onLongPress: widget.onLongPress,
            onHighlightChanged: _setPressed,
            borderRadius: widget.borderRadius,
            child: DecoratedBox(
              decoration: BoxDecoration(
                borderRadius: widget.borderRadius,
                border: Border.all(color: border, width: widget.borderWidth),
              ),
              child: widget.padding != null
                  ? Padding(padding: widget.padding!, child: widget.child)
                  : widget.child,
            ),
          ),
        ),
      ),
    );

    if (widget.semanticLabel != null) {
      return Semantics(
        button: widget.onTap != null,
        label: widget.semanticLabel,
        child: card,
      );
    }
    return card;
  }
}
