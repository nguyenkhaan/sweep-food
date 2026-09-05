import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/formatters/quantity_format.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_result.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_preview.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/cooking_controller.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/custom_usage_controller.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';

/// D-04 — "Điều chỉnh lượng đã dùng". One slider per matched batch (a recipe
/// ingredient can be split across more than one), then deducts the exact
/// amounts and routes to the cook-result screen.
class CustomUsageSheet extends ConsumerStatefulWidget {
  const CustomUsageSheet({
    required this.preview,
    required this.dishName,
    super.key,
  });

  final CookingPreview preview;
  final String dishName;

  static Future<void> show(
    BuildContext context, {
    required CookingPreview preview,
    required String dishName,
  }) async {
    final result = await showAppBottomSheet<CookResult>(
      context,
      builder: (_) => CustomUsageSheet(preview: preview, dishName: dishName),
    );
    if (result != null && context.mounted) {
      context.push(Routes.cookResult, extra: result);
    }
  }

  @override
  ConsumerState<CustomUsageSheet> createState() => _State();
}

class _State extends ConsumerState<CustomUsageSheet> {
  bool _busy = false;

  Future<void> _confirm() async {
    setState(() => _busy = true);
    try {
      final usage = ref.read(customUsageControllerProvider(widget.preview));
      final consumptions = [
        for (final d in widget.preview.proposedDeductions)
          ConsumptionLine(
            recipeIngredientId: d.recipeIngredientId,
            batchId: d.batchId,
            quantity: usage['${d.recipeIngredientId}|${d.batchId}'] ?? d.quantity,
          ),
      ];
      final result = await ref
          .read(cookingControllerProvider.notifier)
          .confirm(
            preview: widget.preview,
            mode: CookMode.custom,
            dishName: widget.dishName,
            consumptions: consumptions,
          );
      if (mounted) Navigator.of(context).pop(result);
    } catch (_) {
      if (!mounted) return;
      setState(() => _busy = false);
      AppSnack.show(context, context.l10n.cookUpdateFailed);
    }
  }

  @override
  Widget build(BuildContext context) {
    final preview = widget.preview;
    final usage = ref.watch(customUsageControllerProvider(preview));
    final notifier = ref.read(customUsageControllerProvider(preview).notifier);
    final pantryItems =
        ref.watch(pantryListControllerProvider).asData?.value ?? const [];
    final byId = {for (final i in pantryItems) i.id: i};

    return SheetBody(
      title: context.l10n.customUsageTitle,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final d in preview.proposedDeductions)
            Padding(
              padding: const EdgeInsets.only(bottom: Gap.sm),
              child: Builder(
                builder: (context) {
                  final item = byId[d.batchId];
                  final name = item?.name ?? context.l10n.catOther;
                  final key = '${d.recipeIngredientId}|${d.batchId}';
                  final value = (usage[key] ?? d.quantity).clamp(
                    0.0,
                    d.quantity == 0 ? 1.0 : d.quantity,
                  );
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(name, style: context.text.titleSmall),
                          ),
                          Text(
                            '${formatQuantity(value, d.unit)}'
                            ' / ${formatQuantity(d.quantity, d.unit)}',
                            style: context.text.labelMedium?.copyWith(
                              color: context.sweep.textSecondary,
                            ),
                          ),
                        ],
                      ),
                      Slider(
                        value: value,
                        max: d.quantity == 0 ? 1 : d.quantity,
                        onChanged: _busy ? null : (v) => notifier.setUsage(d, v),
                      ),
                    ],
                  );
                },
              ),
            ),
          Gap.gapXs,
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _busy ? null : () => Navigator.of(context).pop(),
                  child: Text(context.l10n.commonCancel),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: FilledButton(
                  onPressed: _busy ? null : _confirm,
                  child: _busy
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.4,
                            color: Colors.white,
                          ),
                        )
                      : Text(context.l10n.commonConfirm),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
