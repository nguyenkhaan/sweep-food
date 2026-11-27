import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/app_dialog.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/core/widgets/secondary_button.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_item_controller.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/adjust_quantity_sheet.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/fresh_check_sheet.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';
import 'package:sweepfood/shared/domain/expiry_status.dart';

/// K-02 — Chi tiết nguyên liệu (Concept B · Format 2: Radial Freshness Ring
/// Hero + Unified Storage & Quick Actions Sheet).
class PantryItemDetailScreen extends ConsumerStatefulWidget {
  const PantryItemDetailScreen({required this.itemId, super.key});

  final String itemId;

  @override
  ConsumerState<PantryItemDetailScreen> createState() =>
      _PantryItemDetailScreenState();
}

class _PantryItemDetailScreenState
    extends ConsumerState<PantryItemDetailScreen> {
  bool _busy = false;

  Future<void> _consumeAll(PantryItem item) async {
    setState(() => _busy = true);
    try {
      await ref
          .read(pantryListControllerProvider.notifier)
          .consume(item.id, quantityUsed: item.quantity);
      if (!mounted) return;
      context.pop();
      AppSnack.show(context, context.l10n.pantryConsumedAll(item.name));
    } catch (_) {
      if (!mounted) return;
      setState(() => _busy = false);
      AppSnack.show(context, context.l10n.pantryUpdateFailed);
    }
  }

  Future<void> _delete(PantryItem item) async {
    final l10n = context.l10n;
    final confirmed = await showAppConfirmDialog(
      context,
      title: l10n.pantryDeleteTitle,
      message: l10n.pantryDeleteBody(item.name),
      confirmLabel: l10n.commonDelete,
      cancelLabel: l10n.commonCancel,
      destructive: true,
    );
    if (confirmed != true) return;
    setState(() => _busy = true);
    try {
      await ref.read(pantryListControllerProvider.notifier).delete(item.id);
      if (!mounted) return;
      context.pop();
      AppSnack.show(context, context.l10n.pantryDeleted(item.name));
    } catch (_) {
      if (!mounted) return;
      setState(() => _busy = false);
      AppSnack.show(context, context.l10n.pantryDeleteFailed);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final item = ref.watch(pantryItemByIdProvider(widget.itemId));

    if (item == null) {
      return EmeraldSystemOverlay(
        child: Scaffold(
          backgroundColor: cs.surface,
          body: Column(
            children: [
              EmeraldSplitHeader(title: l10n.pantryTitle),
              Expanded(
                child: EmptyState(
                  illustrationAsset: 'assets/illustrations/empty_search.svg',
                  title: l10n.pantryNotFoundTitle,
                  message: l10n.pantryNotFoundBody,
                  icon: AppIcons.archive,
                ),
              ),
            ],
          ),
        ),
      );
    }

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
        systemNavigationBarColor: cs.surfaceContainerLowest,
        systemNavigationBarIconBrightness:
            Theme.of(context).brightness == Brightness.dark
            ? Brightness.light
            : Brightness.dark,
      ),
      child: Scaffold(
        backgroundColor: cs.surface,
        body: CustomScrollView(
          slivers: [
            // Clean pinned emerald top bar (no duplicate item name)
            SliverAppBar(
              pinned: true,
              automaticallyImplyLeading: false,
              backgroundColor: sweep.heroSurface,
              surfaceTintColor: Colors.transparent,
              elevation: 0,
              scrolledUnderElevation: 0,
              toolbarHeight: 58,
              titleSpacing: Gap.lg,
              title: Row(
                children: [
                  _EmeraldBarButton(
                    icon: AppIcons.arrowLeft,
                    tooltip: 'Quay lại',
                    onPressed: () => context.pop(),
                  ),
                ],
              ),
              actions: [
                _EmeraldBarButton(
                  icon: AppIcons.edit,
                  tooltip: l10n.commonEdit,
                  onPressed: _busy
                      ? null
                      : () => context.push(
                          '${Routes.pantry}/add',
                          extra: item.id,
                        ),
                ),
                const SizedBox(width: Gap.xs),
                Padding(
                  padding: const EdgeInsets.only(right: Gap.lg),
                  child: _EmeraldBarButton(
                    icon: AppIcons.trash,
                    tooltip: l10n.pantryDeleteMenu,
                    onPressed: _busy ? null : () => _delete(item),
                  ),
                ),
              ],
            ),

            // Format 2 · Radial Freshness Ring Hero + Integrated FreshCheck CTA
            SliverToBoxAdapter(
              child: _RadialRingHero(
                item: item,
                onFreshCheck: () => FreshCheckSheet.show(context, item),
              ),
            ),

            // Rising Crisp Sheet · Only 2 cohesive grouped cards
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(
                Gap.lg,
                Gap.xs,
                Gap.lg,
                Gap.xxl,
              ),
              sliver: SliverList.list(
                children: [
                  _StorageInfoGroup(item: item),
                  Gap.gapLg,
                  _QuickActionsGroup(
                    onFindDishes: () {
                      AppHaptics.selection();
                      ref
                          .read(suggestionFilterControllerProvider.notifier)
                          .setPrompt(item.name);
                      context.go(Routes.suggestions);
                    },
                    onHistory: () {
                      AppHaptics.selection();
                      context.push(
                        '${Routes.inventoryLedger}?batchId=${item.id}',
                        extra: item.name,
                      );
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
        bottomNavigationBar: _ActionBar(
          busy: _busy,
          onAdjust: () => AdjustQuantitySheet.show(context, item),
          onConsumeAll: () => _consumeAll(item),
        ),
      ),
    );
  }
}

class _EmeraldBarButton extends StatelessWidget {
  const _EmeraldBarButton({
    required this.icon,
    required this.tooltip,
    required this.onPressed,
  });

  final IconData icon;
  final String tooltip;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return Tooltip(
      message: tooltip,
      child: Material(
        color: sweep.heroSurfaceElevated,
        shape: RoundedRectangleBorder(
          borderRadius: Radii.brMd,
          side: BorderSide(color: sweep.onHeroSurface.withValues(alpha: 0.14)),
        ),
        child: InkWell(
          borderRadius: Radii.brMd,
          onTap: onPressed == null
              ? null
              : () {
                  AppHaptics.selection();
                  onPressed!();
                },
          child: SizedBox(
            width: 40,
            height: 40,
            child: Icon(icon, size: 18, color: sweep.onHeroSurface),
          ),
        ),
      ),
    );
  }
}

/// Format 2 Hero: circular freshness ring on the left, clean identity + inline
/// FreshCheck pill on the right, transitioning smoothly into the rising sheet.
class _RadialRingHero extends StatelessWidget {
  const _RadialRingHero({required this.item, required this.onFreshCheck});

  final PantryItem item;
  final VoidCallback onFreshCheck;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;

    final level = Expiry.levelFromDays(item.daysUntilExpiry);
    final progress = _freshnessFraction(
      item.daysUntilExpiry,
      item.referenceShelfLifeDays,
    );

    final ringColor = switch (level) {
      ExpiryLevel.expired || ExpiryLevel.critical => sweep.ctaWarm,
      ExpiryLevel.soon => sweep.hangCord,
      ExpiryLevel.ok => sweep.onHeroMuted,
    };

    final (String numLabel, String unitLabel) = switch (item.daysUntilExpiry) {
      null => ('—', 'CHƯA RÕ'),
      final d when d < 0 => ('$d', 'QUÁ HẠN'),
      0 => ('0', 'HÔM NAY'),
      final d => ('$d', 'NGÀY'),
    };

    final metaParts = <String>[
      item.quantityLabel,
      item.storageTier.shortLabel(l10n),
      if (item.expiryDate != null) 'HSD ${item.expiryDate!.ddMM}',
    ];

    return DecoratedBox(
      decoration: BoxDecoration(color: sweep.heroSurface),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(
              Gap.lg,
              Gap.xs,
              Gap.lg,
              Gap.lg + 4,
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Animated circular radial freshness gauge (crisp stroke, zero glow)
                SizedBox(
                  width: 84,
                  height: 84,
                  child: TweenAnimationBuilder<double>(
                    tween: Tween<double>(begin: 0, end: progress),
                    duration: AppMotion.resolve(
                      context,
                      const Duration(milliseconds: 680),
                    ),
                    curve: AppMotion.resolveCurve(context, Curves.easeOutCubic),
                    builder: (context, animatedProgress, child) => CustomPaint(
                      painter: _FreshnessRingPainter(
                        progress: animatedProgress,
                        trackColor: sweep.onHeroSurface.withValues(alpha: 0.16),
                        arcColor: ringColor,
                      ),
                      child: child,
                    ),
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.all(10),
                        child: AnimatedSwitcher(
                          duration: AppMotion.resolve(
                            context,
                            context.motion.fast,
                          ),
                          child: Column(
                            key: ValueKey('$numLabel-$unitLabel'),
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              FittedBox(
                                fit: BoxFit.scaleDown,
                                child: Text(
                                  numLabel,
                                  maxLines: 1,
                                  style: AppTypography.tabular(
                                    context.text.titleLarge?.copyWith(
                                      color: sweep.onHeroSurface,
                                      fontWeight: FontWeight.w800,
                                      height: 1.0,
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 2),
                              FittedBox(
                                fit: BoxFit.scaleDown,
                                child: Text(
                                  unitLabel,
                                  maxLines: 1,
                                  style: context.text.labelSmall?.copyWith(
                                    color: sweep.onHeroMuted,
                                    fontSize: 9.5,
                                    fontWeight: FontWeight.w700,
                                    letterSpacing: 0.4,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: Gap.md + 2),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.name,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: context.text.headlineSmall?.copyWith(
                          color: sweep.onHeroSurface,
                          fontWeight: FontWeight.w800,
                          height: 1.18,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        metaParts.join(' · '),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: context.text.bodySmall?.copyWith(
                          color: sweep.onHeroMuted,
                          height: 1.35,
                        ),
                      ),
                      const SizedBox(height: Gap.sm + 2),
                      Material(
                        color: sweep.heroSurfaceElevated,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(Radii.pill),
                          side: BorderSide(
                            color: sweep.onHeroSurface.withValues(alpha: 0.16),
                          ),
                        ),
                        child: InkWell(
                          borderRadius: BorderRadius.circular(Radii.pill),
                          onTap: () {
                            AppHaptics.selection();
                            onFreshCheck();
                          },
                          child: Padding(
                            padding: const EdgeInsets.symmetric(
                              horizontal: Gap.sm + 2,
                              vertical: 7,
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  AppIcons.shield,
                                  size: 14,
                                  color: item.isNearExpiry()
                                      ? sweep.ctaWarm
                                      : sweep.onHeroMuted,
                                ),
                                const SizedBox(width: 6),
                                Flexible(
                                  child: Text(
                                    'Kiểm tra độ tươi',
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: context.text.labelMedium?.copyWith(
                                      color: sweep.onHeroSurface,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 4),
                                Icon(
                                  AppIcons.chevronRight,
                                  size: 14,
                                  color: sweep.onHeroMuted,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Container(
            height: 22,
            decoration: BoxDecoration(
              color: cs.surface,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(28),
              ),
            ),
          ),
        ],
      ),
    );
  }

  static double _freshnessFraction(int? days, int? refDays) {
    if (days == null) return 0.5;
    if (days <= 0) return 0.14;
    final maxDays = (refDays != null && refDays > 0) ? refDays : 14;
    return (days / maxDays).clamp(0.16, 1.0);
  }
}

class _FreshnessRingPainter extends CustomPainter {
  const _FreshnessRingPainter({
    required this.progress,
    required this.trackColor,
    required this.arcColor,
  });

  final double progress;
  final Color trackColor;
  final Color arcColor;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (math.min(size.width, size.height) - 7) / 2;
    const stroke = 6.0;

    canvas.drawCircle(
      center,
      radius,
      Paint()
        ..color = trackColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = stroke,
    );

    final sweepAngle = 2 * math.pi * progress.clamp(0.05, 1.0);
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      sweepAngle,
      false,
      Paint()
        ..color = arcColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = stroke
        ..strokeCap = StrokeCap.round,
    );
  }

  @override
  bool shouldRepaint(covariant _FreshnessRingPainter old) =>
      old.progress != progress ||
      old.trackColor != trackColor ||
      old.arcColor != arcColor;
}

class _StorageInfoGroup extends StatelessWidget {
  const _StorageInfoGroup({required this.item});

  final PantryItem item;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final level = Expiry.levelFromDays(item.daysUntilExpiry);
    final expiryColor = switch (level) {
      ExpiryLevel.expired => sweep.expired.fg,
      ExpiryLevel.critical => sweep.ctaWarm,
      ExpiryLevel.soon => sweep.soon.fg,
      ExpiryLevel.ok => cs.onSurface,
    };

    final rows = <(IconData, String, String, Color?)>[
      (AppIcons.scale, l10n.pantryStatQuantity, item.quantityLabel, null),
      (
        AppIcons.calendar,
        l10n.pantryStatExpiry,
        item.expiryDate?.ddMMyyyy ?? '—',
        expiryColor,
      ),
      (
        AppIcons.forTier(item.storageTier),
        l10n.pantryDetailLocation,
        item.storageTier.label(l10n),
        null,
      ),
      if (item.category.trim().isNotEmpty)
        (
          AppIcons.forCategory(item.category, fallbackName: item.name),
          'Phân loại',
          item.category.trim(),
          null,
        ),
      (AppIcons.clock, l10n.pantryDetailAdded, item.addedAt.ddMMyyyy, null),
      if (item.packedDate != null)
        (
          AppIcons.calendar,
          l10n.pantryDetailPacked,
          item.packedDate!.ddMMyyyy,
          null,
        ),
      (AppIcons.info, l10n.pantryDetailSource, item.source.label(l10n), null),
      if (item.referenceShelfLifeDays != null)
        (
          AppIcons.timer,
          l10n.pantryDetailShelfRef,
          l10n.daysCount(item.referenceShelfLifeDays!),
          null,
        ),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 2, bottom: Gap.xs + 2),
          child: Text(
            l10n.pantryDetailCardTitle,
            style: context.text.titleSmall?.copyWith(
              color: sweep.textSecondary,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: cs.surfaceContainerLowest,
            borderRadius: Radii.brXl,
            border: Border.all(color: sweep.hairline),
            boxShadow: Shadows.e1,
          ),
          child: Column(
            children: [
              for (var i = 0; i < rows.length; i++) ...[
                if (i > 0) Divider(height: 1, color: sweep.hairline),
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: Gap.md,
                    vertical: 13,
                  ),
                  child: Row(
                    children: [
                      Icon(rows[i].$1, size: 16, color: sweep.textTertiary),
                      const SizedBox(width: Gap.sm),
                      Expanded(
                        flex: 5,
                        child: Text(
                          rows[i].$2,
                          style: context.text.bodyMedium?.copyWith(
                            color: sweep.textSecondary,
                          ),
                        ),
                      ),
                      const SizedBox(width: Gap.sm),
                      Expanded(
                        flex: 4,
                        child: Text(
                          rows[i].$3,
                          textAlign: TextAlign.right,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: AppTypography.tabular(
                            context.text.bodyMedium?.copyWith(
                              color: rows[i].$4 ?? cs.onSurface,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _QuickActionsGroup extends StatelessWidget {
  const _QuickActionsGroup({
    required this.onFindDishes,
    required this.onHistory,
  });

  final VoidCallback onFindDishes;
  final VoidCallback onHistory;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 2, bottom: Gap.xs + 2),
          child: Text(
            'Hành động nhanh',
            style: context.text.titleSmall?.copyWith(
              color: sweep.textSecondary,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        Material(
          color: cs.surfaceContainerLowest,
          shape: RoundedRectangleBorder(
            borderRadius: Radii.brXl,
            side: BorderSide(color: sweep.hairline),
          ),
          clipBehavior: Clip.antiAlias,
          child: Column(
            children: [
              _ActionGroupRow(
                icon: AppIcons.cook,
                label: l10n.pantryFindDishes,
                onTap: onFindDishes,
              ),
              Divider(height: 1, color: sweep.hairline),
              _ActionGroupRow(
                icon: AppIcons.history,
                label: 'Lịch sử biến động kho',
                onTap: onHistory,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _ActionGroupRow extends StatelessWidget {
  const _ActionGroupRow({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: Gap.md, vertical: 13),
        child: Row(
          children: [
            Container(
              width: 34,
              height: 34,
              decoration: BoxDecoration(
                color: cs.primaryContainer,
                borderRadius: Radii.brSm,
              ),
              child: Icon(icon, size: 17, color: cs.primary),
            ),
            const SizedBox(width: Gap.sm + 2),
            Expanded(
              child: Text(
                label,
                style: context.text.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            Icon(AppIcons.chevronRight, size: 17, color: sweep.textTertiary),
          ],
        ),
      ),
    );
  }
}

class _ActionBar extends StatelessWidget {
  const _ActionBar({
    required this.busy,
    required this.onAdjust,
    required this.onConsumeAll,
  });

  final bool busy;
  final VoidCallback onAdjust;
  final VoidCallback onConsumeAll;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: cs.surfaceContainerLowest,
        border: Border(top: BorderSide(color: sweep.hairline)),
      ),
      child: SafeArea(
        top: false,
        minimum: const EdgeInsets.fromLTRB(Gap.lg, Gap.sm, Gap.lg, Gap.sm),
        child: Row(
          children: [
            Expanded(
              child: SecondaryButton(
                label: l10n.pantryAdjust,
                icon: AppIcons.filter,
                onPressed: busy ? null : onAdjust,
              ),
            ),
            const SizedBox(width: Gap.sm),
            Expanded(
              child: SizedBox(
                height: 48,
                child: FilledButton.icon(
                  style: FilledButton.styleFrom(
                    backgroundColor: sweep.ctaWarm,
                    foregroundColor: sweep.onCtaWarm,
                    elevation: 0,
                    shadowColor: Colors.transparent,
                    shape: const RoundedRectangleBorder(
                      borderRadius: Radii.brLg,
                    ),
                  ),
                  onPressed: busy
                      ? null
                      : () {
                          AppHaptics.medium();
                          onConsumeAll();
                        },
                  icon: busy
                      ? SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: sweep.onCtaWarm,
                          ),
                        )
                      : const Icon(AppIcons.check, size: 18),
                  label: Text(
                    l10n.pantryConsumeAll,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
