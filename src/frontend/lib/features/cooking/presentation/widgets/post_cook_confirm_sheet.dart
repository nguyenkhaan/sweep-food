import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_result.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_preview.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/cooking_controller.dart';
import 'package:sweepfood/features/cooking/presentation/widgets/custom_usage_sheet.dart';

/// D-03 — "Bạn đã nấu …?" (Concept B · Format 1 Crisp Sheet + Grouped Options).
class PostCookConfirmSheet extends ConsumerStatefulWidget {
  const PostCookConfirmSheet({
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
    final outcome = await showAppBottomSheet<_Outcome>(
      context,
      builder: (_) =>
          PostCookConfirmSheet(preview: preview, dishName: dishName),
    );
    if (outcome == null || !context.mounted) return;
    switch (outcome) {
      case _WantCustom():
        await CustomUsageSheet.show(
          context,
          preview: preview,
          dishName: dishName,
        );
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
            preview: widget.preview,
            mode: mode,
            dishName: widget.dishName,
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
    final sweep = context.sweep;
    final cs = context.colors;

    return SheetBody(
      icon: AppIcons.cook,
      warmIcon: true,
      title: l10n.cookConfirmTitle(widget.dishName),
      subtitle: l10n.cookConfirmSubtitle,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SheetGroupCard(
            child: Column(
              children: [
                _OptionRow(
                  icon: AppIcons.check,
                  iconBg: cs.primaryContainer,
                  iconFg: cs.primary,
                  label: CookMode.exact.label(l10n),
                  description: l10n.cookExactWithServings(
                    widget.preview.servings.round(),
                  ),
                  recommended: true,
                  enabled: !_busy,
                  onTap: () => _confirm(CookMode.exact),
                ),
                Divider(height: 1, color: sweep.hairline),
                _OptionRow(
                  iconText: '½',
                  iconBg: sweep.subtleFill,
                  iconFg: sweep.textSecondary,
                  label: CookMode.half.label(l10n),
                  description: CookMode.half.description(l10n),
                  enabled: !_busy,
                  onTap: () => _confirm(CookMode.half),
                ),
                Divider(height: 1, color: sweep.hairline),
                _OptionRow(
                  icon: AppIcons.trash,
                  iconBg: sweep.culinaryAccentBg,
                  iconFg: sweep.ctaWarm,
                  label: CookMode.all.label(l10n),
                  description: CookMode.all.description(l10n),
                  enabled: !_busy,
                  onTap: () => _confirm(CookMode.all),
                ),
                Divider(height: 1, color: sweep.hairline),
                _OptionRow(
                  icon: AppIcons.filter,
                  iconBg: sweep.subtleFill,
                  iconFg: sweep.textSecondary,
                  label: CookMode.custom.label(l10n),
                  description: CookMode.custom.description(l10n),
                  enabled: !_busy,
                  onTap: () => Navigator.of(context).pop(const _WantCustom()),
                ),
              ],
            ),
          ),
          if (_busy) ...[
            Gap.gapSm,
            ClipRRect(
              borderRadius: BorderRadius.circular(Radii.pill),
              child: const LinearProgressIndicator(minHeight: 4),
            ),
          ],
        ],
      ),
    );
  }
}

class _OptionRow extends StatelessWidget {
  const _OptionRow({
    required this.label,
    required this.description,
    required this.iconBg,
    required this.iconFg,
    required this.onTap,
    this.icon,
    this.iconText,
    this.recommended = false,
    this.enabled = true,
  });

  final String label;
  final String description;
  final Color iconBg;
  final Color iconFg;
  final VoidCallback onTap;
  final IconData? icon;
  final String? iconText;
  final bool recommended;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    final rowBg = recommended
        ? Color.alphaBlend(
            cs.primaryContainer.withValues(alpha: 0.32),
            cs.surfaceContainerLowest,
          )
        : Colors.transparent;

    return Material(
      color: rowBg,
      child: InkWell(
        onTap: !enabled
            ? null
            : () {
                AppHaptics.selection();
                onTap();
              },
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: Gap.md,
            vertical: Gap.sm + 4,
          ),
          child: Row(
            children: [
              Container(
                width: 36,
                height: 36,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: iconBg,
                  borderRadius: Radii.brMd,
                ),
                child: iconText != null
                    ? Text(
                        iconText!,
                        style: context.text.titleSmall?.copyWith(
                          color: iconFg,
                          fontWeight: FontWeight.w800,
                        ),
                      )
                    : Icon(icon, size: 17, color: iconFg),
              ),
              const SizedBox(width: Gap.sm + 2),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            label,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: context.text.titleSmall?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                        if (recommended) ...[
                          const SizedBox(width: 6),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 7,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: cs.primaryContainer,
                              borderRadius: BorderRadius.circular(Radii.pill),
                            ),
                            child: Text(
                              context.l10n.commonRecommended,
                              style: context.text.labelSmall?.copyWith(
                                letterSpacing: 0,
                                color: cs.primary,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      description,
                      style: context.text.bodySmall?.copyWith(
                        color: sweep.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: Gap.xs),
              Icon(
                AppIcons.chevronRight,
                size: 17,
                color: sweep.textTertiary,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
