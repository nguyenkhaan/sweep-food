import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';

/// Displays a remote recipe image with smooth fade-in, optional [Hero]
/// transition, and graceful fallback to a warm culinary placeholder if
/// [imageUrl] is null/empty or fails to load.
///
/// Limits decode memory overhead via [cacheWidth] (sized to display width).
class RecipeImage extends StatelessWidget {
  const RecipeImage({
    this.imageUrl,
    this.imageProvider,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
    this.iconSize,
    this.iconColor,
    this.backgroundColor,
    this.borderRadius,
    this.heroTag,
    super.key,
  });

  final String? imageUrl;
  final ImageProvider? imageProvider;
  final double? width;
  final double? height;
  final BoxFit fit;
  final double? iconSize;
  final Color? iconColor;
  final Color? backgroundColor;
  final BorderRadius? borderRadius;
  final Object? heroTag;

  Widget _buildPlaceholder(BuildContext context) {
    final sweep = Theme.of(context).extension<SweepColors>();
    final colors = Theme.of(context).colorScheme;
    final bg = backgroundColor ?? sweep?.subtleFill ?? colors.surfaceContainer;
    final fg = iconColor ?? sweep?.textTertiary ?? colors.onSurfaceVariant;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        gradient: backgroundColor == null
            ? LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  bg,
                  Color.alphaBlend(
                    colors.primary.withValues(alpha: isDark ? 0.14 : 0.08),
                    bg,
                  ),
                ],
              )
            : null,
        color: backgroundColor,
      ),
      alignment: Alignment.center,
      child: Icon(AppIcons.utensils, size: iconSize ?? 32, color: fg),
    );
  }

  Widget _fadeInFrame(
    BuildContext context,
    Widget child,
    int? frame,
    bool wasSynchronouslyLoaded,
  ) {
    if (wasSynchronouslyLoaded || MediaQuery.disableAnimationsOf(context)) {
      return frame == null ? _buildPlaceholder(context) : child;
    }
    return Stack(
      fit: StackFit.passthrough,
      children: [
        if (frame == null) _buildPlaceholder(context),
        AnimatedOpacity(
          opacity: frame == null ? 0 : 1,
          duration: AppMotion.resolve(
            context,
            const Duration(milliseconds: 220),
          ),
          curve: Curves.easeOut,
          child: child,
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final url = imageUrl?.trim();
    final hasProvider = imageProvider != null;
    final hasUrl = url != null && url.isNotEmpty;

    Widget content;
    if (!hasProvider && !hasUrl) {
      content = _buildPlaceholder(context);
    } else {
      content = LayoutBuilder(
        builder: (context, constraints) {
          final dpr = MediaQuery.maybeDevicePixelRatioOf(context) ?? 1.0;
          int? targetCacheWidth;
          if (width != null && width! > 0) {
            targetCacheWidth = (width! * dpr).round();
          } else if (constraints.hasBoundedWidth &&
              constraints.maxWidth.isFinite &&
              constraints.maxWidth > 0) {
            targetCacheWidth = (constraints.maxWidth * dpr).round();
          }

          if (hasProvider) {
            return Image(
              image: imageProvider!,
              width: width,
              height: height,
              fit: fit,
              frameBuilder: _fadeInFrame,
              loadingBuilder: (context, child, loadingProgress) {
                if (loadingProgress == null) return child;
                return _buildPlaceholder(context);
              },
              errorBuilder: (context, error, stackTrace) {
                return _buildPlaceholder(context);
              },
            );
          }

          return Image.network(
            url!,
            width: width,
            height: height,
            fit: fit,
            cacheWidth: targetCacheWidth,
            frameBuilder: _fadeInFrame,
            loadingBuilder: (context, child, loadingProgress) {
              if (loadingProgress == null) return child;
              return _buildPlaceholder(context);
            },
            errorBuilder: (context, error, stackTrace) {
              return _buildPlaceholder(context);
            },
          );
        },
      );
    }

    if (borderRadius != null) {
      content = ClipRRect(borderRadius: borderRadius!, child: content);
    }

    if (heroTag != null) {
      content = Hero(tag: heroTag!, child: content);
    }
    return content;
  }
}
