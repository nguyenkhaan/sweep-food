import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
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

/// D-04 — "Điều chỉnh lượng đã dùng" (Concept B · Format 1 Crisp Sheet).
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
            quantity:
                usage['${d.recipeIngredientId}|${d.batchId}'] ?? d.quantity,
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
    final sweep = context.sweep;
    final cs = context.colors;

    return SheetBody(
      icon: AppIcons.filter,
      title: context.l10n.customUsageTitle,
      subtitle: widget.dishName,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          ConstrainedBox(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.sizeOf(context).height * 0.48,
            ),
            child: SingleChildScrollView(
              child: SheetGroupCard(
                child: Column(
                  children: [
                    for (
                      var idx = 0;
                      idx < preview.proposedDeductions.length;
                      idx++
                    ) ...[
                      if (idx > 0) Divider(height: 1, color: sweep.hairline),
                      Builder(
                        builder: (context) {
                          final d = preview.proposedDeductions[idx];
                          final item = byId[d.batchId];
                          final name = item?.name ?? context.l10n.catOther;
                          final key = '${d.recipeIngredientId}|${d.batchId}';
                          final value = (usage[key] ?? d.quantity).clamp(
                            0.0,
                            d.quantity == 0 ? 1.0 : d.quantity,
                          );
                          return Padding(
                            padding: const EdgeInsets.fromLTRB(
                              Gap.md,
                              Gap.sm + 4,
                              Gap.md,
                              Gap.xs,
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        name,
                                        style: context.text.titleSmall
                                            ?.copyWith(
                                              fontWeight: FontWeight.w700,
                                            ),
                                      ),
                                    ),
                                    Text(
                                      '${formatQuantity(value, d.unit)}'
                                      ' / ${formatQuantity(d.quantity, d.unit)}',
                                      style: AppTypography.tabular(
                                        context.text.labelMedium?.copyWith(
                                          color: cs.primary,
                                          fontWeight: FontWeight.w700,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                                SliderTheme(
                                  data: SliderTheme.of(context).copyWith(
                                    activeTrackColor: cs.primary,
                                    inactiveTrackColor: sweep.subtleFill,
                                    thumbColor: cs.primary,
                                    trackHeight: 5,
                                  ),
                                  child: Slider(
                                    value: value,
                                    max: d.quantity == 0 ? 1 : d.quantity,
                                    onChanged: _busy
                                        ? null
                                        : (v) => notifier.setUsage(d, v),
                                  ),
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
          Gap.gapMd,
          Row(
            children: [
              Expanded(
                flex: 4,
                child: SheetCancelButton(
                  label: context.l10n.commonCancel,
                  onPressed: _busy ? null : () => Navigator.of(context).pop(),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                flex: 6,
                child: SheetWarmButton(
                  label: context.l10n.commonConfirm,
                  icon: AppIcons.check,
                  loading: _busy,
                  onPressed: _busy ? null : _confirm,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
