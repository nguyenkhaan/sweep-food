import 'package:flutter/material.dart';

/// SweepFood's official tomato-viewfinder brand emblem (`sf_icon.png`).
///
/// Renders bare by default (no background tile or border box) so the mark sits
/// directly on any surface without unnecessary layered containers.
class AppLogo extends StatelessWidget {
  const AppLogo({
    this.size = 32,
    this.borderRadius,
    this.backgroundColor,
    this.padding,
    super.key,
  });

  final double size;
  final BorderRadius? borderRadius;
  final Color? backgroundColor;
  final EdgeInsetsGeometry? padding;

  @override
  Widget build(BuildContext context) {
    final dpr = MediaQuery.maybeDevicePixelRatioOf(context) ?? 2.0;
    final cachePx = (size * dpr).round().clamp(48, 512);
    final image = Image.asset(
      'assets/images/sf_icon.png',
      width: size,
      height: size,
      fit: BoxFit.contain,
      cacheWidth: cachePx,
      semanticLabel: 'SweepFood',
    );

    if (backgroundColor == null) return image;

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: borderRadius ?? BorderRadius.circular(size * 0.28),
      ),
      clipBehavior: Clip.antiAlias,
      padding: padding ?? EdgeInsets.all((size * 0.12).clamp(2.0, 10.0)),
      child: image,
    );
  }
}
