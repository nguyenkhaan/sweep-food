import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/expiry_badge.dart';
import 'package:frontend/shared/domain/expiry_status.dart';
import 'package:frontend/shared/domain/storage_tier.dart';

/// Pantry list row (K-01, H-01 "Cần dùng sớm").
///
/// Takes primitives (not a `PantryItem`) so it compiles before the entity
/// exists — M1 maps entity → these params.
class PantryItemCard extends StatelessWidget {
  const PantryItemCard({
    required this.name,
    required this.subtitle,
    required this.daysUntilExpiry,
    this.tier,
    this.leadingIcon = Icons.eco_outlined,
    this.selected,
    this.onSelectedChanged,
    this.onTap,
    this.onMore,
    this.compact = false,
    super.key,
  });

  final String name;

  /// e.g. "500g · Rau củ".
  final String subtitle;
  final int? daysUntilExpiry;
  final StorageTier? tier;
  final IconData leadingIcon;

  /// When non-null a checkbox is shown (multi-select mode).
  final bool? selected;
  final ValueChanged<bool?>? onSelectedChanged;

  final VoidCallback? onTap;
  final VoidCallback? onMore;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final level = Expiry.levelFromDays(daysUntilExpiry);
    final urgent = level == ExpiryLevel.expired || level == ExpiryLevel.critical;

    return Material(
      color: context.colors.surfaceContainerLowest,
      borderRadius: Radii.brLg,
      child: InkWell(
        onTap: onTap,
        borderRadius: Radii.brLg,
        child: Container(
          padding: const EdgeInsets.all(Gap.sm),
          decoration: BoxDecoration(
            borderRadius: Radii.brLg,
            // Uniform border only — a non-uniform Border with a borderRadius
            // throws during paint. Urgent items get a full coloured outline.
            border: Border.all(
              color: urgent ? context.sweep.critical.fg : context.sweep.hairline,
              width: urgent ? 1.5 : 1,
            ),
          ),
          child: Row(
            children: [
              if (selected != null) ...[
                Checkbox(value: selected, onChanged: onSelectedChanged),
                const SizedBox(width: 2),
              ],
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: context.sweep.subtleFill,
                  borderRadius: Radii.brMd,
                ),
                child: Icon(leadingIcon, size: 20, color: context.sweep.textTertiary),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: context.text.titleSmall,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 2),
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            subtitle,
                            style: context.text.bodyMedium
                                ?.copyWith(color: context.sweep.textTertiary, fontSize: 12),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(width: Gap.xs),
              ExpiryBadge(daysUntilExpiry: daysUntilExpiry),
              if (onMore != null)
                IconButton(
                  visualDensity: VisualDensity.compact,
                  icon: const Icon(Icons.more_vert_rounded, size: 18),
                  onPressed: onMore,
                ),
            ],
          ),
        ),
      ),
    );
  }
}
