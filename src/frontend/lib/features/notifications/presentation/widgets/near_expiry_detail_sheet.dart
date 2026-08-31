import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_bottom_sheet.dart';
import 'package:frontend/core/widgets/expiry_badge.dart';
import 'package:frontend/core/widgets/primary_button.dart';
import 'package:frontend/core/widgets/secondary_button.dart';
import 'package:frontend/features/notifications/domain/entities/expiry_alert.dart';
import 'package:frontend/features/pantry/presentation/controllers/pantry_item_controller.dart';
import 'package:frontend/features/pantry/presentation/widgets/adjust_quantity_sheet.dart';
import 'package:go_router/go_router.dart';

/// T-02 Chi tiết cảnh báo cận hạn. Built from the pantry item itself — item
/// header + a storage tip + two actions ("Đánh dấu đã dùng" / "Xem gợi ý").
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
    final item = ref.watch(pantryItemByIdProvider(pantryItemId));

    if (item == null) {
      return const SheetBody(
        child: Padding(
          padding: EdgeInsets.symmetric(vertical: Gap.lg),
          child: Text('Không tìm thấy nguyên liệu này trong kho.'),
        ),
      );
    }

    return SheetBody(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: const BoxDecoration(
                  color: BrandPalette.green100,
                  borderRadius: Radii.brMd,
                ),
                child: const Icon(
                  Icons.eco_rounded,
                  color: BrandPalette.green700,
                ),
              ),
              Gap.gapSm,
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(item.name, style: context.text.titleMedium),
                    Text(
                      '${item.quantityLabel} · ${item.category} · '
                      '${item.storageTier.shortLabel}',
                      style: context.text.bodySmall?.copyWith(
                        color: context.sweep.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              ExpiryBadge(daysUntilExpiry: item.daysUntilExpiry),
            ],
          ),
          Gap.gapMd,
          Container(
            padding: const EdgeInsets.all(Gap.md),
            decoration: BoxDecoration(
              color: context.sweep.subtleFill,
              borderRadius: Radii.brMd,
            ),
            child: Text(
              ExpiryTips.forCategory(item.category),
              style: context.text.bodySmall?.copyWith(height: 1.5),
            ),
          ),
          Gap.gapLg,
          Row(
            children: [
              Expanded(
                child: SecondaryButton(
                  label: 'Đánh dấu đã dùng',
                  onPressed: () {
                    Navigator.of(context).pop();
                    AdjustQuantitySheet.show(context, item);
                  },
                ),
              ),
              Gap.gapSm,
              Expanded(
                child: PrimaryButton(
                  label: 'Xem gợi ý',
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
