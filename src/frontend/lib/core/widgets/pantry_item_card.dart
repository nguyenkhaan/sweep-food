import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/freshness_bar.dart';
import 'package:sweepfood/core/widgets/tactile_card.dart';
import 'package:sweepfood/shared/domain/expiry_status.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// Format 1 — Pantry Ticket list card (K-01).
///
/// Features a left urgency bar, tappable category icon that flips into an
/// emerald checkmark for multi-select (removing permanent checkbox clutter),
/// clean inline quantity + storage metadata with integrated freshness progress,
/// and a right-aligned countdown stub separated by a dashed ticket hairline.
class PantryItemCard extends StatelessWidget {
  const PantryItemCard({
    required this.name,
    required this.subtitle,
    required this.daysUntilExpiry,
    this.tier,
    this.category,
    this.referenceShelfLifeDays,
    this.leadingIcon = AppIcons.leaf,
    this.selected,
    this.onSelectedChanged,
    this.onTap,
    this.onMore,
    this.compact = false,
    super.key,
  });

  final String name;
  final String subtitle;
  final int? daysUntilExpiry;
  final StorageTier? tier;
  final String? category;
  final int? referenceShelfLifeDays;
  final IconData leadingIcon;

  /// When non-null, tapping the leading icon toggles multi-select state.
  final bool? selected;
  final ValueChanged<bool?>? onSelectedChanged;

  final VoidCallback? onTap;
  final VoidCallback? onMore;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final cs = context.colors;
    final l10n = context.l10n;
    final level = Expiry.levelFromDays(daysUntilExpiry);
    final isSelected = selected ?? false;
    final catColors = sweep.categoryForLabel(
      category ?? '',
      fallbackName: name,
    );

    final urgencyColor = switch (level) {
      ExpiryLevel.expired => sweep.expired.fg,
      ExpiryLevel.critical => sweep.ctaWarm,
      ExpiryLevel.soon => sweep.soon.fg,
      ExpiryLevel.ok => cs.primary,
    };

    final bgColor = isSelected
        ? Color.alphaBlend(
            cs.primaryContainer.withValues(alpha: 0.42),
            cs.surfaceContainerLowest,
          )
        : cs.surfaceContainerLowest;

    final borderColor = isSelected ? cs.primary : sweep.hairline;

    final selectable = selected != null && onSelectedChanged != null;

    return TactileCard(
      color: bgColor,
      borderColor: borderColor,
      borderWidth: isSelected ? 1.5 : 1,
      padding: EdgeInsets.zero,
      boxShadow: Shadows.e1,
      onTap: onTap,
      onLongPress: !selectable
          ? null
          : () {
              AppHaptics.medium();
              onSelectedChanged!(!isSelected);
            },
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 1. Left urgency accent stripe
            Container(
              width: 4,
              margin: const EdgeInsets.symmetric(vertical: 10),
              decoration: BoxDecoration(
                color: isSelected ? cs.primary : urgencyColor,
                borderRadius: const BorderRadius.horizontal(
                  right: Radius.circular(4),
                ),
              ),
            ),

            // 2. Main body: tappable category icon + title/meta/bar
            Expanded(
              child: Padding(
                padding: EdgeInsets.fromLTRB(
                  Gap.sm + 2,
                  compact ? Gap.sm : Gap.sm + 3,
                  Gap.sm,
                  compact ? Gap.sm : Gap.sm + 3,
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    _CategorySelectTile(
                      icon: leadingIcon,
                      bg: catColors.bg,
                      fg: catColors.fg,
                      selected: isSelected,
                      selectable: selectable,
                      onToggle: selectable
                          ? () {
                              AppHaptics.selection();
                              onSelectedChanged!(!isSelected);
                            }
                          : null,
                    ),
                    const SizedBox(width: Gap.sm + 2),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.center,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  name,
                                  style: context.text.titleSmall?.copyWith(
                                    fontWeight: FontWeight.w700,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              if (onMore != null)
                                IconButton(
                                  visualDensity: VisualDensity.compact,
                                  constraints: const BoxConstraints(),
                                  padding: const EdgeInsets.only(left: Gap.xs),
                                  icon: const Icon(
                                    AppIcons.moreVertical,
                                    size: 18,
                                  ),
                                  onPressed: onMore,
                                ),
                            ],
                          ),
                          const SizedBox(height: 3),
                          _InlineMetaRow(
                            subtitle: subtitle,
                            tier: compact ? null : tier,
                            tierLabel: tier?.shortLabel(l10n),
                          ),
                          if (!compact && daysUntilExpiry != null) ...[
                            const SizedBox(height: 7),
                            FreshnessBar(
                              daysUntilExpiry: daysUntilExpiry,
                              referenceDays: referenceShelfLifeDays,
                              height: 3.5,
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // 3. Dashed vertical ticket divider + right countdown stub
            if (!compact) ...[
              CustomPaint(
                size: const Size(1, double.infinity),
                painter: _DashedVerticalDividerPainter(color: sweep.hairline),
              ),
              _CountdownTicketStub(
                daysUntilExpiry: daysUntilExpiry,
                color: urgencyColor,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _CategorySelectTile extends StatelessWidget {
  const _CategorySelectTile({
    required this.icon,
    required this.bg,
    required this.fg,
    required this.selected,
    required this.selectable,
    this.onToggle,
  });

  final IconData icon;
  final Color bg;
  final Color fg;
  final bool selected;
  final bool selectable;
  final VoidCallback? onToggle;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final flipDuration = AppMotion.resolve(
      context,
      const Duration(milliseconds: 360),
    );
    final flipCurve = AppMotion.resolveCurve(context, Curves.easeOutBack);

    final tile = TweenAnimationBuilder<double>(
      tween: Tween<double>(end: selected ? math.pi : 0.0),
      duration: flipDuration,
      curve: flipCurve,
      builder: (context, angle, _) {
        final showBack = angle > math.pi / 2;
        final matrix = Matrix4.identity()
          ..setEntry(3, 2, 0.0022)
          ..rotateY(angle);
        return Transform(
          alignment: Alignment.center,
          transform: matrix,
          child: Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: showBack ? cs.primary : bg,
              borderRadius: Radii.brMd,
            ),
            child: Transform(
              alignment: Alignment.center,
              transform: showBack
                  ? (Matrix4.identity()..rotateY(math.pi))
                  : Matrix4.identity(),
              child: Icon(
                showBack ? AppIcons.check : icon,
                size: 20,
                color: showBack ? cs.onPrimary : fg,
              ),
            ),
          ),
        );
      },
    );

    if (!selectable) return tile;

    return Semantics(
      button: true,
      selected: selected,
      label: selected ? 'Bỏ chọn nguyên liệu' : 'Chọn nguyên liệu',
      child: GestureDetector(
        key: const ValueKey('pantry-select-toggle'),
        behavior: HitTestBehavior.opaque,
        onTap: onToggle,
        child: tile,
      ),
    );
  }
}

class _InlineMetaRow extends StatelessWidget {
  const _InlineMetaRow({required this.subtitle, this.tier, this.tierLabel});

  final String subtitle;
  final StorageTier? tier;
  final String? tierLabel;

  @override
  Widget build(BuildContext context) {
    final color = context.sweep.textSecondary;
    final style = context.text.bodySmall?.copyWith(color: color);

    if (tier == null || tierLabel == null) {
      return Text(
        subtitle,
        style: style,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      );
    }

    return Row(
      children: [
        Flexible(
          child: Text(
            subtitle,
            style: style,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 5),
          child: Text('·', style: style),
        ),
        Icon(AppIcons.forTier(tier!), size: 12.5, color: color),
        const SizedBox(width: 3),
        Flexible(
          child: Text(
            tierLabel!,
            style: style,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}

class _CountdownTicketStub extends StatelessWidget {
  const _CountdownTicketStub({
    required this.daysUntilExpiry,
    required this.color,
  });

  final int? daysUntilExpiry;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final (String value, String unit, Color tint) = switch (daysUntilExpiry) {
      null => ('—', 'CHƯA RÕ', sweep.textTertiary),
      final d when d < 0 => ('$d', 'QUÁ HẠN', color),
      0 => ('0', 'HÔM NAY', color),
      final d => ('$d', 'NGÀY NỮA', color),
    };

    return ConstrainedBox(
      constraints: const BoxConstraints(minWidth: 74, maxWidth: 86),
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.xs + 2,
          vertical: Gap.sm,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            FittedBox(
              fit: BoxFit.scaleDown,
              child: Text(
                value,
                maxLines: 1,
                style: AppTypography.tabular(
                  context.text.titleMedium?.copyWith(
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                    color: tint,
                    height: 1.05,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 3),
            FittedBox(
              fit: BoxFit.scaleDown,
              child: Text(
                unit,
                maxLines: 1,
                style: context.text.labelSmall?.copyWith(
                  fontSize: 9.5,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.3,
                  color: tint,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DashedVerticalDividerPainter extends CustomPainter {
  const _DashedVerticalDividerPainter({required this.color});

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 1.0;

    const dash = 4.0;
    const gap = 3.5;
    double y = 10.0;
    final endY = size.height - 10.0;
    while (y < endY) {
      canvas.drawLine(
        Offset(0, y),
        Offset(0, (y + dash).clamp(0, endY)),
        paint,
      );
      y += dash + gap;
    }
  }

  @override
  bool shouldRepaint(covariant _DashedVerticalDividerPainter old) =>
      old.color != color;
}
