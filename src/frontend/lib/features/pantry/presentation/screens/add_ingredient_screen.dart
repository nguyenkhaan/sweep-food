import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/catalog/domain/entities/ingredient.dart';
import 'package:sweepfood/features/catalog/presentation/controllers/ingredient_search_controller.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/add_ingredient_controller.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// K-03 — Thêm / Sửa nguyên liệu (thủ công).
///
/// `editItemId == null` → add mode; otherwise the form is seeded from that item.
class AddIngredientScreen extends ConsumerStatefulWidget {
  const AddIngredientScreen({this.editItemId, super.key});

  final String? editItemId;

  @override
  ConsumerState<AddIngredientScreen> createState() =>
      _AddIngredientScreenState();
}

class _AddIngredientScreenState extends ConsumerState<AddIngredientScreen> {
  final _nameCtrl = TextEditingController();
  final _categoryCtrl = TextEditingController();
  final _qtyCtrl = TextEditingController();
  final _nameFocus = FocusNode();

  bool _busy = false;
  String _query = '';

  String? get _key => widget.editItemId;
  bool get _isEditing => widget.editItemId != null;
  AddIngredientController get _ctrl =>
      ref.read(addIngredientControllerProvider(_key).notifier);

  @override
  void initState() {
    super.initState();
    final draft = ref.read(addIngredientControllerProvider(_key));
    _nameCtrl.text = draft.name;
    _categoryCtrl.text = draft.category;
    if (draft.quantity > 0) _qtyCtrl.text = _fmtQty(draft.quantity);
    _nameFocus.addListener(() {
      if (!_nameFocus.hasFocus && mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _categoryCtrl.dispose();
    _qtyCtrl.dispose();
    _nameFocus.dispose();
    super.dispose();
  }

  static String _fmtQty(double n) => n == n.roundToDouble()
      ? n.round().toString()
      : n.toStringAsFixed(1).replaceAll('.', ',');

  double _stepFor(MeasurementUnit unit) => switch (unit) {
    MeasurementUnit.gram || MeasurementUnit.milliliter => 50,
    MeasurementUnit.kilogram || MeasurementUnit.liter => 0.5,
    _ => 1,
  };

  void _bumpQty(double delta) {
    final draft = ref.read(addIngredientControllerProvider(_key));
    final next = (draft.quantity + delta).clamp(0, 999999).toDouble();
    _ctrl.setQuantity(next);
    _qtyCtrl.text = next > 0 ? _fmtQty(next) : '';
    _qtyCtrl.selection = TextSelection.collapsed(offset: _qtyCtrl.text.length);
  }

  void _pickIngredient(Ingredient ing) {
    _ctrl.applyIngredient(ing);
    _nameCtrl.text = ing.name;
    _categoryCtrl.text = ing.category;
    _query = '';
    _nameFocus.unfocus();
    // Suggest an expiry date if we now know a reference shelf life.
    _maybeAutoExpiry();
    setState(() {});
  }

  void _maybeAutoExpiry() {
    final draft = ref.read(addIngredientControllerProvider(_key));
    if (draft.expiryDate != null) return;
    final days = draft.referenceShelfLifeDays;
    final from = draft.packedDate ?? DateTime.now();
    if (days != null) _ctrl.setExpiryDate(from.add(Duration(days: days)));
  }

  Future<void> _pickDate({
    required DateTime? initial,
    required ValueChanged<DateTime?> onPicked,
  }) async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: initial ?? now,
      firstDate: DateTime(now.year - 1),
      lastDate: DateTime(now.year + 5),
    );
    if (picked != null) onPicked(picked);
  }

  Future<void> _submit() async {
    setState(() => _busy = true);
    try {
      final item = await _ctrl.submit();
      if (!mounted) return;
      context.pop();
      AppSnack.show(
        context,
        _isEditing
            ? context.l10n.pantryItemUpdated(item.name)
            : context.l10n.pantryItemAdded(item.name),
      );
    } catch (_) {
      if (!mounted) return;
      setState(() => _busy = false);
      AppSnack.show(context, context.l10n.pantrySaveFailed);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final draft = ref.watch(addIngredientControllerProvider(_key));
    final showSuggestions =
        _nameFocus.hasFocus &&
        _query.trim().isNotEmpty &&
        draft.ingredientId == null;

    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? l10n.pantryEditTitle : l10n.pantryAddTitle),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
        children: [
          _Label(l10n.pantryFieldName),
          TextField(
            controller: _nameCtrl,
            focusNode: _nameFocus,
            textCapitalization: TextCapitalization.sentences,
            decoration: InputDecoration(hintText: l10n.pantryFieldNameHint),
            onChanged: (v) {
              _ctrl.setName(v);
              setState(() => _query = v);
            },
          ),
          if (showSuggestions)
            _SuggestionList(query: _query, onPick: _pickIngredient),
          Gap.gapMd,
          _Label(l10n.pantryFieldCategory),
          TextField(
            controller: _categoryCtrl,
            textCapitalization: TextCapitalization.sentences,
            decoration: InputDecoration(hintText: l10n.pantryFieldCategoryHint),
            onChanged: _ctrl.setCategory,
          ),
          Gap.gapMd,
          _Label(l10n.pantryStatQuantity),
          Row(
            children: [
              _StepButton(
                icon: Icons.remove_rounded,
                onTap: draft.quantity <= 0
                    ? null
                    : () => _bumpQty(-_stepFor(draft.unit)),
              ),
              const SizedBox(width: Gap.xs),
              Expanded(
                child: TextField(
                  controller: _qtyCtrl,
                  textAlign: TextAlign.center,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'[0-9.,]')),
                  ],
                  decoration: const InputDecoration(hintText: '0'),
                  onChanged: (v) => _ctrl.setQuantity(
                    double.tryParse(v.replaceAll(',', '.')) ?? 0,
                  ),
                ),
              ),
              const SizedBox(width: Gap.xs),
              _StepButton(
                icon: Icons.add_rounded,
                onTap: () => _bumpQty(_stepFor(draft.unit)),
              ),
              const SizedBox(width: Gap.sm),
              _UnitDropdown(
                value: draft.unit,
                onChanged: (u) => _ctrl.setUnit(u),
              ),
            ],
          ),
          Gap.gapMd,
          _Label(l10n.pantryFieldStorage),
          Wrap(
            spacing: Gap.xs,
            children: [
              for (final tier in StorageTier.values)
                ChoiceChip(
                  label: Text(tier.shortLabel(l10n)),
                  selected: draft.storageTier == tier,
                  onSelected: (_) => _ctrl.setTier(tier),
                ),
            ],
          ),
          Gap.gapMd,
          Row(
            children: [
              Expanded(
                child: _DateField(
                  label: l10n.pantryDetailPacked,
                  value: draft.packedDate,
                  onTap: () => _pickDate(
                    initial: draft.packedDate,
                    onPicked: (d) {
                      _ctrl.setPackedDate(d);
                      _maybeAutoExpiry();
                    },
                  ),
                  onClear: draft.packedDate == null
                      ? null
                      : () => _ctrl.setPackedDate(null),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: _DateField(
                  label: l10n.pantryFieldExpiry,
                  value: draft.expiryDate,
                  onTap: () => _pickDate(
                    initial: draft.expiryDate,
                    onPicked: (d) => _ctrl.setExpiryDate(d),
                  ),
                  onClear: draft.expiryDate == null
                      ? null
                      : () => _ctrl.setExpiryDate(null),
                ),
              ),
            ],
          ),
          Gap.gapXl,
          PrimaryButton(
            label: _isEditing ? l10n.pantrySaveChanges : l10n.pantryAddToPantry,
            loading: _busy,
            onPressed: draft.isValid && !_busy ? _submit : null,
          ),
        ],
      ),
    );
  }
}

class _Label extends StatelessWidget {
  const _Label(this.text);

  final String text;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: Gap.xxs),
    child: Text(text.toUpperCase(), style: context.text.labelSmall),
  );
}

class _SuggestionList extends ConsumerWidget {
  const _SuggestionList({required this.query, required this.onPick});

  final String query;
  final ValueChanged<Ingredient> onPick;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final results = ref.watch(ingredientSearchProvider(query));
    return results.maybeWhen(
      data: (list) {
        if (list.isEmpty) return const SizedBox.shrink();
        return Padding(
          padding: const EdgeInsets.only(top: Gap.xs),
          child: Wrap(
            spacing: Gap.xs,
            runSpacing: Gap.xxs,
            children: [
              for (final ing in list.take(8))
                ActionChip(
                  avatar: const Icon(Icons.add_rounded, size: 16),
                  label: Text(ing.name),
                  onPressed: () => onPick(ing),
                ),
            ],
          ),
        );
      },
      orElse: () => const SizedBox.shrink(),
    );
  }
}

class _StepButton extends StatelessWidget {
  const _StepButton({required this.icon, required this.onTap});

  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return IconButton.outlined(
      visualDensity: VisualDensity.compact,
      onPressed: onTap,
      icon: Icon(icon, size: 18),
    );
  }
}

class _UnitDropdown extends StatelessWidget {
  const _UnitDropdown({required this.value, required this.onChanged});

  final MeasurementUnit value;
  final ValueChanged<MeasurementUnit> onChanged;

  @override
  Widget build(BuildContext context) {
    return DropdownButton<MeasurementUnit>(
      value: value,
      underline: const SizedBox.shrink(),
      onChanged: (u) {
        if (u != null) onChanged(u);
      },
      items: [
        for (final u in MeasurementUnit.values)
          DropdownMenuItem(value: u, child: Text(u.label)),
      ],
    );
  }
}

class _DateField extends StatelessWidget {
  const _DateField({
    required this.label,
    required this.value,
    required this.onTap,
    this.onClear,
  });

  final String label;
  final DateTime? value;
  final VoidCallback onTap;
  final VoidCallback? onClear;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: Radii.brSm,
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: label,
          suffixIcon: onClear != null
              ? IconButton(
                  icon: const Icon(Icons.close_rounded, size: 18),
                  onPressed: onClear,
                )
              : const Icon(Icons.event_outlined, size: 18),
        ),
        child: Text(
          value?.ddMMyyyy ?? context.l10n.commonNotChosen,
          style: value == null
              ? context.text.bodyMedium?.copyWith(
                  color: context.sweep.textTertiary,
                )
              : context.text.bodyMedium,
        ),
      ),
    );
  }
}
