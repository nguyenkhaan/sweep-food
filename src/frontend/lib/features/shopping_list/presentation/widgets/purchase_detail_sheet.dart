import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_purchase_draft.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// Shown when checking off a shopping-list item as bought (Concept B · Format 1).
class PurchaseDetailSheet extends StatefulWidget {
  const PurchaseDetailSheet({super.key});

  static Future<ShoppingPurchaseDraft?> show(BuildContext context) =>
      showAppBottomSheet<ShoppingPurchaseDraft>(
        context,
        builder: (_) => const PurchaseDetailSheet(),
      );

  @override
  State<PurchaseDetailSheet> createState() => _PurchaseDetailSheetState();
}

class _PurchaseDetailSheetState extends State<PurchaseDetailSheet> {
  StorageTier _tier = StorageTier.fridge;
  DateTime? _expiry;
  int? _presetDays;
  final _price = TextEditingController();

  @override
  void dispose() {
    _price.dispose();
    super.dispose();
  }

  Future<void> _pickExpiry() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: _expiry ?? now,
      firstDate: now,
      lastDate: now.add(const Duration(days: 3650)),
    );
    if (picked != null) {
      setState(() {
        _expiry = picked;
        _presetDays = null;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final cs = context.colors;
    final sweep = context.sweep;

    return SheetBody(
      icon: AppIcons.shopping,
      title: l10n.shoppingPurchaseTitle,
      subtitle: l10n.shoppingPurchaseSubtitle,
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'VỊ TRÍ BẢO QUẢN',
              style: context.text.labelSmall?.copyWith(
                letterSpacing: 0.6,
                color: sweep.textTertiary,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: Gap.xs + 2),
            Wrap(
              spacing: Gap.xs,
              runSpacing: Gap.xs,
              children: [
                for (final tier in StorageTier.values)
                  _SelectPill(
                    icon: AppIcons.forTier(tier),
                    label: tier.shortLabel(l10n),
                    selected: _tier == tier,
                    onTap: () {
                      AppHaptics.selection();
                      setState(() => _tier = tier);
                    },
                  ),
              ],
            ),
            Gap.gapMd,
            Text(
              'HẠN SỬ DỤNG DỰ KIẾN',
              style: context.text.labelSmall?.copyWith(
                letterSpacing: 0.6,
                color: sweep.textTertiary,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: Gap.xs + 2),
            Material(
              color: cs.surfaceContainerLowest,
              shape: RoundedRectangleBorder(
                borderRadius: Radii.brLg,
                side: BorderSide(color: sweep.hairline),
              ),
              child: InkWell(
                borderRadius: Radii.brLg,
                onTap: _pickExpiry,
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: Gap.md,
                    vertical: 12,
                  ),
                  child: Row(
                    children: [
                      Icon(AppIcons.calendar, size: 18, color: cs.primary),
                      const SizedBox(width: Gap.sm),
                      Expanded(
                        child: Text(
                          _expiry == null
                              ? l10n.shoppingPurchaseExpiryPick
                              : _expiry!.ddMMyyyy,
                          style: context.text.bodyMedium?.copyWith(
                            color: _expiry == null
                                ? sweep.textSecondary
                                : cs.onSurface,
                            fontWeight: _expiry == null
                                ? FontWeight.w500
                                : FontWeight.w700,
                          ),
                        ),
                      ),
                      if (_expiry != null)
                        GestureDetector(
                          onTap: () {
                            AppHaptics.selection();
                            setState(() {
                              _expiry = null;
                              _presetDays = null;
                            });
                          },
                          child: Icon(
                            AppIcons.close,
                            size: 17,
                            color: sweep.textTertiary,
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: Gap.xs + 2),
            Wrap(
              spacing: Gap.xs,
              runSpacing: Gap.xs,
              children: [
                for (final days in const [3, 7, 14])
                  _SelectPill(
                    label: l10n.purchasePresetDays(days),
                    selected: _presetDays == days,
                    onTap: () {
                      AppHaptics.selection();
                      setState(() {
                        _presetDays = days;
                        _expiry = DateTime.now().add(Duration(days: days));
                      });
                    },
                  ),
              ],
            ),
            Gap.gapMd,
            TextField(
              controller: _price,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: l10n.shoppingPurchasePriceLabel,
                suffixText: '₫',
              ),
            ),
            Gap.gapMd,
            SheetWarmButton(
              icon: AppIcons.check,
              label: l10n.shoppingPurchaseConfirm,
              onPressed: () => Navigator.of(context).pop(
                ShoppingPurchaseDraft(
                  storageTier: _tier,
                  expiryDate: _expiry,
                  priceVnd: int.tryParse(_price.text.trim()),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SelectPill extends StatelessWidget {
  const _SelectPill({
    required this.label,
    required this.selected,
    required this.onTap,
    this.icon,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: AppMotion.resolve(context, context.motion.fast),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? sweep.heroSurface : cs.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(Radii.pill),
          border: Border.all(
            color: selected ? sweep.heroSurface : sweep.hairline,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[
              Icon(
                icon,
                size: 14,
                color: selected ? sweep.onHeroSurface : sweep.textSecondary,
              ),
              const SizedBox(width: 5),
            ],
            Text(
              label,
              style: context.text.labelMedium?.copyWith(
                color: selected ? sweep.onHeroSurface : sweep.textSecondary,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
