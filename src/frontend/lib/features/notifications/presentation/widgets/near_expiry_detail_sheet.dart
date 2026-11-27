import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/expiry_badge.dart';
import 'package:sweepfood/features/notifications/domain/entities/expiry_alert.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_item_controller.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/adjust_quantity_sheet.dart';

/// T-02 Chi tiết cảnh báo cận hạn (Concept B · Format 1 Crisp Sheet).
class NearExpiryDetailSheet extends ConsumerWidget {
  const NearExpiryDetailSheet({required this.pantryItemId, super.key});

  final String pantryItemId;

  static Future<void> show(BuildContext context, String pantryItemId) =>
      showAppBottomSheet(
        context,
        builder: (_) => NearExpiryDetailSheet(pantryItemId: pantryItemId),
      );

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final item = ref.watch(pantryItemByIdProvider(pantryItemId));

    if (item == null) {
      return SheetBody(
        icon: AppIcons.archive,
        title: l10n.pantryTitle,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: Gap.md),
          child: Text(
            l10n.nearExpiryNotFound,
            style: context.text.bodyMedium?.copyWith(
              color: sweep.textSecondary,
            ),
          ),
        ),
      );
    }

    final catColors = sweep.categoryForLabel(
      item.category,
      fallbackName: item.name,
    );

    return SheetBody(
      icon: AppIcons.forCategory(item.category, fallbackName: item.name),
      iconBg: catColors.bg,
      iconFg: catColors.fg,
      title: item.name,
      subtitle:
          '${item.quantityLabel} · ${item.storageTier.shortLabel(l10n)}',
      trailing: ExpiryBadge(daysUntilExpiry: item.daysUntilExpiry),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SheetGroupCard(
            padding: const EdgeInsets.all(Gap.md),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: 1),
                  child: Icon(
                    AppIcons.lightbulb,
                    size: 16,
                    color: sweep.ctaWarm,
                  ),
                ),
                const SizedBox(width: Gap.xs + 2),
                Expanded(
                  child: Text(
                    ExpiryTips.forCategory(item.category, l10n),
                    style: context.text.bodySmall?.copyWith(
                      color: sweep.textSecondary,
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Gap.gapMd,
          Row(
            children: [
              Expanded(
                child: SheetCancelButton(
                  label: l10n.nearExpiryMarkUsed,
                  onPressed: () {
                    Navigator.of(context).pop();
                    AdjustQuantitySheet.show(context, item);
                  },
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: SheetWarmButton(
                  icon: AppIcons.cook,
                  label: l10n.nearExpirySeeSuggestions,
                  onPressed: () {
                    Navigator.of(context).pop();
                    context.go(Routes.suggestions);
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
