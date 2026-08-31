import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/widgets/app_bottom_sheet.dart';
import 'package:frontend/core/widgets/primary_button.dart';
import 'package:frontend/features/settings/presentation/controllers/preferences_controller.dart';
import 'package:frontend/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:frontend/features/shopping_list/presentation/controllers/shopping_list_controller.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';

/// B-02 Thêm món thủ công.
class AddShoppingItemSheet extends ConsumerStatefulWidget {
  const AddShoppingItemSheet({super.key});

  static Future<void> show(BuildContext context) => showAppBottomSheet(
        context,
        builder: (_) => const AddShoppingItemSheet(),
      );

  @override
  ConsumerState<AddShoppingItemSheet> createState() => _State();
}

class _State extends ConsumerState<AddShoppingItemSheet> {
  final _name = TextEditingController();
  final _qty = TextEditingController(text: '1');
  final _category = TextEditingController();
  late MeasurementUnit _unit = ref.read(preferencesControllerProvider).defaultUnit;
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
    await ref.read(shoppingListControllerProvider.notifier).addManualItem(
          ShoppingListItemDraft(
            name: name,
            quantity: qty,
            unit: _unit,
            category: _category.text.trim().isEmpty
                ? 'Khác'
                : _category.text.trim(),
          ),
        );
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return SheetBody(
      title: 'Thêm món',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: _name,
            autofocus: true,
            textCapitalization: TextCapitalization.sentences,
            decoration: const InputDecoration(labelText: 'Tên món'),
          ),
          Gap.gapSm,
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _qty,
                  keyboardType:
                      const TextInputType.numberWithOptions(decimal: true),
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'[0-9.,]')),
                  ],
                  decoration: const InputDecoration(labelText: 'Số lượng'),
                ),
              ),
              Gap.gapSm,
              Expanded(
                child: DropdownButtonFormField<MeasurementUnit>(
                  initialValue: _unit,
                  decoration: const InputDecoration(labelText: 'Đơn vị'),
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
            decoration: const InputDecoration(
              labelText: 'Danh mục (tùy chọn)',
              hintText: 'Rau củ, Thịt & hải sản, …',
            ),
          ),
          Gap.gapLg,
          PrimaryButton(
            label: 'Thêm vào danh sách',
            loading: _busy,
            onPressed: _busy ? null : _submit,
          ),
        ],
      ),
    );
  }
}
