import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_purchase_draft.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// Shown when checking off a shopping-list item as bought — the backend
/// needs this to create the resulting inventory batch. See
/// `docs/api-contract.md` §8.
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
    if (picked != null) setState(() => _expiry = picked);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return SheetBody(
      title: l10n.shoppingPurchaseTitle,
      subtitle: l10n.shoppingPurchaseSubtitle,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Wrap(
            spacing: Gap.xs,
            children: [
              for (final tier in StorageTier.values)
                ChoiceChip(
                  label: Text(tier.shortLabel(l10n)),
                  selected: _tier == tier,
                  onSelected: (_) => setState(() => _tier = tier),
                ),
            ],
          ),
          Gap.gapMd,
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _pickExpiry,
                  icon: const Icon(Icons.event_outlined),
                  label: Text(
                    _expiry == null
                        ? l10n.shoppingPurchaseExpiryPick
                        : _expiry!.ddMM,
                  ),
                ),
              ),
              if (_expiry != null)
                IconButton(
                  onPressed: () => setState(() => _expiry = null),
                  icon: const Icon(Icons.close_rounded),
                ),
            ],
          ),
          Gap.gapMd,
          TextField(
            controller: _price,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(
              labelText: l10n.shoppingPurchasePriceLabel,
            ),
          ),
          Gap.gapLg,
          PrimaryButton(
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
    );
  }
}
