import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_colors.dart';

/// Displays a remote recipe image with graceful fallback to a restaurant
/// placeholder if [imageUrl] is null/empty or if image loading fails.
///
/// Limits decode memory overhead via [cacheWidth] (sized to display width)
/// and avoids spinner flicker by holding the placeholder until the first frame loads.
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

  Widget _buildPlaceholder(BuildContext context) {
    final sweep = Theme.of(context).extension<SweepColors>();
    final bg = backgroundColor ?? sweep?.subtleFill ?? const Color(0xFFEFF1EC);
    final fg = iconColor ?? sweep?.textTertiary ?? const Color(0xFF8A8D87);

    return Container(
      width: width,
      height: height,
      color: bg,
      alignment: Alignment.center,
      child: Icon(
        Icons.restaurant_rounded,
        size: iconSize ?? 34,
        color: fg,
      ),
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
      return ClipRRect(
        borderRadius: borderRadius!,
        child: content,
      );
    }
    return content;
  }
}
