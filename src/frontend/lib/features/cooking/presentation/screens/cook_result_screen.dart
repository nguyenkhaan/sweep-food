import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_result.dart';
import 'package:sweepfood/features/cooking/presentation/widgets/leftover_save_sheet.dart';

/// D-05 / D-07 — "Đã cập nhật kho": before→after per ingredient plus the
/// waste-avoided feedback. No money figure (spec: no price data).
class CookResultScreen extends StatelessWidget {
  const CookResultScreen({required this.result, super.key});

  final CookResult result;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Scaffold(
      appBar: AppBar(automaticallyImplyLeading: false),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xxl),
        children: [
          Center(
            child: Column(
              children: [
                Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    color: context.colors.primaryContainer,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    Icons.check_rounded,
                    size: 30,
                    color: context.colors.primary,
                  ),
                ),
                Gap.gapSm,
                Text(l10n.cookResultTitle, style: context.text.titleLarge),
              ],
            ),
          ),
          Gap.gapLg,
          if (result.nearExpiryUsedCount > 0) _SaveBanner(result: result),
          Gap.gapMd,
          _ChangesCard(result: result),
          if (result.leftoverServings > 0) ...[
            Gap.gapMd,
            OutlinedButton.icon(
              onPressed: () => LeftoverSaveSheet.show(
                context,
                dishId: result.dishId,
                dishName: result.dishName,
                initialServings: result.leftoverServings,
              ),
              icon: const Icon(Icons.save_alt_rounded, size: 18),
              label: Text(
                l10n.cookResultSaveLeftovers(result.leftoverServings),
              ),
            ),
          ],
        ],
      ),
      bottomNavigationBar: SafeArea(
        minimum: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.sm),
        child: Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () => context.go(Routes.pantry),
                child: Text(l10n.cookResultViewPantry),
              ),
            ),
            const SizedBox(width: Gap.sm),
            Expanded(
              child: FilledButton(
                onPressed: () => context.go(Routes.suggestions),
                child: Text(l10n.commonDone),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SaveBanner extends StatelessWidget {
  const _SaveBanner({required this.result});

  final CookResult result;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final kg = result.wasteAvoidedKg;
    final kgText = kg > 0
        ? l10n.cookResultWasteKgSuffix(
            kg.toStringAsFixed(1).replaceAll('.', ','),
          )
        : '';
    return Container(
      padding: const EdgeInsets.all(Gap.sm + 2),
      decoration: BoxDecoration(
        color: context.colors.primaryContainer,
        borderRadius: Radii.brLg,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.trending_up_rounded,
            size: 18,
            color: context.colors.onPrimaryContainer,
          ),
          const SizedBox(width: Gap.xs),
          Expanded(
            child: Text.rich(
              TextSpan(
                style: context.text.bodyMedium?.copyWith(
                  color: context.colors.onPrimaryContainer,
                  height: 1.4,
                ),
                children: [
                  TextSpan(text: l10n.cookResultUsedNearExpiryPrefix),
                  TextSpan(
                    text: l10n.cookResultUsedNearExpiryCount(
                      result.nearExpiryUsedCount,
                    ),
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  TextSpan(text: kgText),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ChangesCard extends StatelessWidget {
  const _ChangesCard({required this.result});

  final CookResult result;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brLg,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(l10n.cookResultChangesHeader, style: context.text.labelSmall),
          Gap.gapXs,
          for (final (i, c) in result.changes.indexed)
            Padding(
              padding: EdgeInsets.only(
                top: i == 0 ? Gap.xxs : Gap.xs,
                bottom: i == result.changes.length - 1 ? 0 : Gap.xs,
              ),
              child: Row(
                children: [
                  Expanded(child: Text(c.name, style: context.text.bodyMedium)),
                  Text(
                    c.beforeLabel,
                    style: context.text.bodyMedium?.copyWith(
                      color: context.sweep.textTertiary,
                    ),
                  ),
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 6),
                    child: Icon(Icons.arrow_forward_rounded, size: 14),
                  ),
                  Text(
                    c.afterLabel,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                ],
              ),
            ),
          if (result.lowStockNames.isNotEmpty) ...[
            Gap.gapSm,
            Container(
              padding: const EdgeInsets.all(Gap.xs),
              decoration: BoxDecoration(
                color: context.sweep.soon.bg,
                borderRadius: Radii.brSm,
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.warning_amber_rounded,
                    size: 15,
                    color: context.sweep.soon.fg,
                  ),
                  const SizedBox(width: Gap.xs),
                  Expanded(
                    child: Text(
                      l10n.cookResultLowStock(result.lowStockNames.join(', ')),
                      style: context.text.labelMedium?.copyWith(
                        color: context.sweep.soon.fg,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: () => context.go(Routes.shopping),
                    child: Text(l10n.commonBuyShort),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
