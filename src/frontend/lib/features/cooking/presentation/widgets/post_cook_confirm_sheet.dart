import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_result.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/cooking_controller.dart';
import 'package:sweepfood/features/cooking/presentation/widgets/custom_usage_sheet.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';

/// D-03 — "Bạn đã nấu …?". Pick a consumption mode; exact/half/all deduct stock
/// straight away, "Tự điều chỉnh" opens the per-ingredient sheet (D-04).
class PostCookConfirmSheet extends ConsumerStatefulWidget {
  const PostCookConfirmSheet({required this.dish, super.key});

  final Dish dish;

  /// Opens the sheet, then routes to the cook-result screen (D-05/D-07) or the
  /// custom-usage sheet depending on what the user chose.
  static Future<void> show(BuildContext context, {required Dish dish}) async {
    final outcome = await showAppBottomSheet<_Outcome>(
      context,
      builder: (_) => PostCookConfirmSheet(dish: dish),
    );
    if (outcome == null || !context.mounted) return;
    switch (outcome) {
      case _WantCustom():
        await CustomUsageSheet.show(context, dish: dish);
      case _Cooked(:final result):
        context.push(Routes.cookResult, extra: result);
    }
  }

  @override
  ConsumerState<PostCookConfirmSheet> createState() => _State();
}

sealed class _Outcome {
  const _Outcome();
}

class _WantCustom extends _Outcome {
  const _WantCustom();
}

class _Cooked extends _Outcome {
  const _Cooked(this.result);
  final CookResult result;
}

class _State extends ConsumerState<PostCookConfirmSheet> {
  bool _busy = false;

  Future<void> _confirm(CookMode mode) async {
    setState(() => _busy = true);
    try {
      final result = await ref
          .read(cookingControllerProvider.notifier)
          .confirm(
            CookConfirmation(
              dishId: widget.dish.id,
              mode: mode,
              servingsCooked: widget.dish.servings,
            ),
            dishName: widget.dish.name,
          );
      if (mounted) Navigator.of(context).pop(_Cooked(result));
    } catch (_) {
      if (!mounted) return;
      setState(() => _busy = false);
      AppSnack.show(context, context.l10n.cookUpdateFailed);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return SheetBody(
      title: l10n.cookConfirmTitle(widget.dish.name),
      subtitle: l10n.cookConfirmSubtitle,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          _Option(
            icon: Icons.check_rounded,
            label: CookMode.exact.label(l10n),
            description: l10n.cookExactWithServings(widget.dish.servings),
            recommended: true,
            enabled: !_busy,
            onTap: () => _confirm(CookMode.exact),
          ),
          _Option(
            iconText: '½',
            label: CookMode.half.label(l10n),
            description: CookMode.half.description(l10n),
            enabled: !_busy,
            onTap: () => _confirm(CookMode.half),
          ),
          _Option(
            icon: Icons.delete_sweep_outlined,
            label: CookMode.all.label(l10n),
            description: CookMode.all.description(l10n),
            enabled: !_busy,
            onTap: () => _confirm(CookMode.all),
          ),
          _Option(
            icon: Icons.tune_rounded,
            label: CookMode.custom.label(l10n),
            description: CookMode.custom.description(l10n),
            enabled: !_busy,
            onTap: () => Navigator.of(context).pop(const _WantCustom()),
          ),
          if (_busy) ...[Gap.gapSm, const LinearProgressIndicator()],
        ],
      ),
    );
  }
}

class _Option extends StatelessWidget {
  const _Option({
    required this.label,
    required this.description,
    required this.onTap,
    this.icon,
    this.iconText,
    this.recommended = false,
    this.enabled = true,
  });

  final String label;
  final String description;
  final VoidCallback onTap;
  final IconData? icon;
  final String? iconText;
  final bool recommended;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      enabled: enabled,
      leading: Container(
        width: 34,
        height: 34,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: context.colors.primaryContainer,
          borderRadius: Radii.brSm,
        ),
        child: iconText != null
            ? Text(
                iconText!,
                style: context.text.titleSmall?.copyWith(
                  color: context.colors.primary,
                  fontWeight: FontWeight.w700,
                ),
              )
            : Icon(icon, size: 17, color: context.colors.primary),
      ),
      title: Row(
        children: [
          Flexible(child: Text(label, style: context.text.titleSmall)),
          if (recommended) ...[
            const SizedBox(width: 6),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
              decoration: BoxDecoration(
                color: context.colors.primaryContainer,
                borderRadius: BorderRadius.circular(Radii.pill),
              ),
              child: Text(
                context.l10n.commonRecommended,
                style: context.text.labelSmall?.copyWith(
                  letterSpacing: 0,
                  color: context.colors.primary,
                ),
              ),
            ),
          ],
        ],
      ),
      subtitle: Text(description),
      trailing: const Icon(Icons.chevron_right_rounded),
      onTap: enabled ? onTap : null,
    );
  }
}
