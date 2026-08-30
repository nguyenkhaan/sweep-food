import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/utils/formatters/quantity_format.dart';
import 'package:frontend/core/widgets/app_bottom_sheet.dart';
import 'package:frontend/core/widgets/app_snackbar.dart';
import 'package:frontend/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:frontend/features/cooking/domain/entities/cook_result.dart';
import 'package:frontend/features/cooking/presentation/controllers/cooking_controller.dart';
import 'package:frontend/features/cooking/presentation/controllers/custom_usage_controller.dart';
import 'package:frontend/features/dishes/domain/entities/dish.dart';
import 'package:go_router/go_router.dart';

/// D-04 — "Điều chỉnh lượng đã dùng". One slider per ingredient, then deducts
/// the exact amounts and routes to the cook-result screen.
class CustomUsageSheet extends ConsumerStatefulWidget {
  const CustomUsageSheet({required this.dish, super.key});

  final Dish dish;

  static Future<void> show(BuildContext context, {required Dish dish}) async {
    final result = await showAppBottomSheet<CookResult>(
      context,
      builder: (_) => CustomUsageSheet(dish: dish),
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
      final usage = ref.read(customUsageControllerProvider(widget.dish.id));
      final result = await ref
          .read(cookingControllerProvider.notifier)
          .confirm(
            CookConfirmation(
              dishId: widget.dish.id,
              mode: CookMode.custom,
              servingsCooked: widget.dish.servings,
              customUsage: usage,
            ),
            dishName: widget.dish.name,
          );
      if (mounted) Navigator.of(context).pop(result);
    } catch (_) {
      if (!mounted) return;
      setState(() => _busy = false);
      AppSnack.show(context, 'Không cập nhật được kho. Thử lại.');
    }
  }

  @override
  Widget build(BuildContext context) {
    final dishId = widget.dish.id;
    final usage = ref.watch(customUsageControllerProvider(dishId));
    final notifier = ref.read(customUsageControllerProvider(dishId).notifier);

    return SheetBody(
      title: 'Điều chỉnh lượng đã dùng',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final ing in widget.dish.mainIngredients)
            Padding(
              padding: const EdgeInsets.only(bottom: Gap.sm),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(ing.name, style: context.text.titleSmall),
                      ),
                      Text(
                        '${formatQuantity(usage[ing.name] ?? ing.quantity, ing.unit)}'
                        ' / ${formatQuantity(ing.quantity, ing.unit)}',
                        style: context.text.labelMedium?.copyWith(
                          color: context.sweep.textSecondary,
                        ),
                      ),
                    ],
                  ),
                  Slider(
                    value: (usage[ing.name] ?? ing.quantity)
                        .clamp(0.0, ing.quantity == 0 ? 1.0 : ing.quantity),
                    max: ing.quantity == 0 ? 1 : ing.quantity,
                    onChanged: _busy
                        ? null
                        : (v) => notifier.setUsage(ing.name, v),
                  ),
                ],
              ),
            ),
          Gap.gapXs,
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _busy ? null : () => Navigator.of(context).pop(),
                  child: const Text('Hủy'),
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
                      : const Text('Xác nhận'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
