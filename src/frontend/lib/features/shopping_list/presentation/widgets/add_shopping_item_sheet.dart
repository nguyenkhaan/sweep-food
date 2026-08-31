import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_bottom_sheet.dart';
import 'package:frontend/core/widgets/primary_button.dart';
import 'package:frontend/features/settings/presentation/controllers/preferences_controller.dart';
import 'package:frontend/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:frontend/features/shopping_list/presentation/controllers/shopping_list_controller.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';

/// B-02 Thêm món thủ công.
class AddShoppingItemSheet extends ConsumerStatefulWidget {
  const AddShoppingItemSheet({super.key});

  static Future<void> show(BuildContext context) =>
      showAppBottomSheet(context, builder: (_) => const AddShoppingItemSheet());

  @override
  ConsumerState<AddShoppingItemSheet> createState() => _State();
}

class _State extends ConsumerState<AddShoppingItemSheet> {
  final _name = TextEditingController();
  final _qty = TextEditingController(text: '1');
  final _category = TextEditingController();
  late MeasurementUnit _unit = ref
      .read(preferencesControllerProvider)
      .defaultUnit;
  bool _busy = false;

  @override
  void dispose() {
    _name.dispose();
    _qty.dispose();
    _category.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final name = _name.text.trim();
    final qty = double.tryParse(_qty.text.replaceAll(',', '.')) ?? 0;
    if (name.isEmpty || qty <= 0) return;
    setState(() => _busy = true);
    await ref
        .read(shoppingListControllerProvider.notifier)
        .addManualItem(
          ShoppingListItemDraft(
            name: name,
            quantity: qty,
            unit: _unit,
            category: _category.text.trim().isEmpty
                ? context.l10n.catOther
                : _category.text.trim(),
          ),
        );
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return SheetBody(
      title: l10n.shoppingAddItem,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: _name,
            autofocus: true,
            textCapitalization: TextCapitalization.sentences,
            decoration: InputDecoration(labelText: l10n.shoppingItemName),
          ),
          Gap.gapSm,
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _qty,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'[0-9.,]')),
                  ],
                  decoration: InputDecoration(
                    labelText: l10n.pantryStatQuantity,
                  ),
                ),
              ),
              Gap.gapSm,
              Expanded(
                child: DropdownButtonFormField<MeasurementUnit>(
                  initialValue: _unit,
                  decoration: InputDecoration(labelText: l10n.reviewUnit),
                  items: [
                    for (final u in MeasurementUnit.values)
                      DropdownMenuItem(value: u, child: Text(u.label)),
                  ],
                  onChanged: (u) => setState(() => _unit = u ?? _unit),
                ),
              ),
            ],
          ),
          Gap.gapSm,
          TextField(
            controller: _category,
            textCapitalization: TextCapitalization.sentences,
            decoration: InputDecoration(
              labelText: l10n.shoppingCategoryOptional,
              hintText: l10n.shoppingCategoryHint,
            ),
          ),
          Gap.gapLg,
          PrimaryButton(
            label: l10n.shoppingAddToList,
            loading: _busy,
            onPressed: _busy ? null : _submit,
          ),
        ],
      ),
    );
  }
}
