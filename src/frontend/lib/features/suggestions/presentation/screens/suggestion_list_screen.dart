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
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/core/widgets/loading_skeleton.dart';
import 'package:sweepfood/core/widgets/recipe_image.dart';
import 'package:sweepfood/core/widgets/staggered_reveal.dart';
import 'package:sweepfood/core/widgets/suggestion_card.dart';
import 'package:sweepfood/core/widgets/tactile_card.dart';
import 'package:sweepfood/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/features/suggestions/data/datasources/suggestion_remote_data_source.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';
import 'package:sweepfood/features/suggestions/presentation/widgets/score_breakdown_sheet.dart';
import 'package:sweepfood/features/suggestions/presentation/widgets/suggestion_card_chips.dart';

/// S-01 — Ranked dish suggestions (Concept B · Format 1: Emerald Split Hero,
/// Featured #1 spotlight card + compact horizontal editorial cards for #2+).
class SuggestionListScreen extends ConsumerWidget {
  const SuggestionListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(suggestionListControllerProvider);
    final aiHealth = ref.watch(aiServiceHealthProvider);
    final hasActivePantry =
        ref
            .watch(pantryListControllerProvider)
            .asData
            ?.value
            .any((item) => item.status == PantryItemStatus.active) ??
        false;
    final cs = context.colors;
    final sweep = context.sweep;
    final count = async.asData?.value.length;

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
        body: Column(
          children: [
            _SuggestionsEmeraldHeader(count: count, health: aiHealth),
            if (aiHealth.hasError) _AiStatusBanner(health: aiHealth),
            Expanded(
              child: RefreshIndicator(
                color: sweep.ctaWarm,
                onRefresh: () => ref
                    .read(suggestionListControllerProvider.notifier)
                    .refresh(),
                child: AsyncValueWidget<List<DishSuggestion>>(
                  value: async,
                  onRetry: () =>
                      ref.invalidate(suggestionListControllerProvider),
                  loading: const DelayedSkeleton(child: SuggestionSkeleton()),
                  data: (items) =>
                      _List(items: items, hasActivePantry: hasActivePantry),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SuggestionsEmeraldHeader extends StatelessWidget {
  const _SuggestionsEmeraldHeader({required this.health, this.count});

  final AsyncValue<AiServiceHealthDto> health;
  final int? count;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final subtitle = count != null && count! > 0
        ? l10n.suggestionsCaption(count!)
        : 'Ưu tiên nguyên liệu sẵn có và sắp hết hạn';

    return DecoratedBox(
      decoration: BoxDecoration(color: sweep.heroSurface),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SafeArea(
            bottom: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(
                Gap.lg,
                Gap.sm,
                Gap.lg,
                Gap.md,
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n.suggestionsTitle,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: context.text.headlineSmall?.copyWith(
                            color: sweep.onHeroSurface,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          subtitle,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: context.text.bodySmall?.copyWith(
                            color: sweep.onHeroMuted,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: Gap.sm),
                  _EngineStatusPill(health: health),
                ],
              ),
            ),
          ),
          Container(
            height: 20,
            decoration: BoxDecoration(
              color: cs.surface,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(26),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _EngineStatusPill extends StatelessWidget {
  const _EngineStatusPill({required this.health});

  final AsyncValue<AiServiceHealthDto> health;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final ready = health.asData?.value.isReady == true;
    final failed = health.hasError;

    final fg = failed ? sweep.ctaWarm : sweep.onHeroMuted;
    final label = ready
        ? 'Sẵn sàng'
        : failed
        ? 'Ngoại tuyến'
        : 'Đang tải…';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Gap.sm, vertical: 6),
      decoration: BoxDecoration(
        color: sweep.heroSurfaceElevated,
        borderRadius: BorderRadius.circular(Radii.pill),
        border: Border.all(color: sweep.onHeroSurface.withValues(alpha: 0.14)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            failed ? AppIcons.warning : AppIcons.suggestions,
            size: 14,
            color: fg,
          ),
          const SizedBox(width: 5),
          Text(
            label,
            style: context.text.labelSmall?.copyWith(
              letterSpacing: 0,
              color: sweep.onHeroSurface,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

enum _QuickFilter { all, nearExpiry, readyToCook, quick }

class _List extends StatefulWidget {
  const _List({required this.items, required this.hasActivePantry});

  final List<DishSuggestion> items;
  final bool hasActivePantry;

  @override
  State<_List> createState() => _ListState();
}

class _ListState extends State<_List> {
  _QuickFilter _filter = _QuickFilter.all;

  List<DishSuggestion> get _filtered {
    return switch (_filter) {
      _QuickFilter.all => widget.items,
      _QuickFilter.nearExpiry =>
        widget.items.where((s) => s.nearExpiryCount > 0).toList(),
      _QuickFilter.readyToCook =>
        widget.items.where((s) => s.toBuyCount == 0).toList(),
      _QuickFilter.quick =>
        widget.items.where((s) => s.dish.totalTimeMin <= 20).toList(),
    };
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final items = widget.items;

    if (items.isEmpty) {
      if (widget.hasActivePantry) {
        return ListView(
          padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
          children: [
            EmptyState(
              title: l10n.suggestionsEmptyFilteredTitle,
              message: l10n.suggestionsEmptyFilteredBody,
              icon: AppIcons.filter,
              actionLabel: l10n.pantryAddIngredient,
              onAction: () => showAddEntryChooser(context),
            ),
            Center(
              child: OutlinedButton.icon(
                onPressed: () => context.push(Routes.settingsNutritionProfile),
                icon: const Icon(AppIcons.shield, size: 18),
                label: Text(l10n.suggestionsReviewProfileCta),
              ),
            ),
            Gap.gapMd,
            const _InlineDisclaimer(),
          ],
        );
      }

      return ListView(
        children: [
          const SizedBox(height: 48),
          EmptyState(
            illustrationAsset: 'assets/illustrations/empty_pantry.svg',
            title: l10n.suggestionsEmptyTitle,
            message: l10n.suggestionsEmptyBody,
            actionLabel: l10n.pantryAddIngredient,
            onAction: () => showAddEntryChooser(context),
          ),
        ],
      );
    }

    final filtered = _filtered;
    final filterLabels = <(_QuickFilter, String)>[
      (_QuickFilter.all, l10n.suggestionsFilterAll),
      (_QuickFilter.nearExpiry, l10n.suggestionsFilterNearExpiry),
      (_QuickFilter.readyToCook, l10n.suggestionsFilterReadyToCook),
      (_QuickFilter.quick, l10n.suggestionsFilterQuick),
    ];

    return ListView(
      padding: const EdgeInsets.fromLTRB(Gap.lg, 0, Gap.lg, 96),
      children: [
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              for (final (kind, label) in filterLabels)
                Padding(
                  padding: const EdgeInsets.only(right: Gap.xs),
                  child: ChoiceChip(
                    label: Text(label),
                    selected: _filter == kind,
                    showCheckmark: false,
                    onSelected: (_) {
                      AppHaptics.selection();
                      setState(() => _filter = kind);
                    },
                    selectedColor: cs.primary,
                    backgroundColor: cs.surfaceContainerLowest,
                    labelStyle: context.text.labelMedium?.copyWith(
                      color: _filter == kind
                          ? cs.onPrimary
                          : sweep.textSecondary,
                      fontWeight: _filter == kind
                          ? FontWeight.w700
                          : FontWeight.w500,
                    ),
                    side: BorderSide(
                      color: _filter == kind ? cs.primary : sweep.hairline,
                    ),
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: Gap.xs),
        const _InlineDisclaimer(),
        const SizedBox(height: Gap.sm),
        if (filtered.isEmpty)
          Padding(
            padding: const EdgeInsets.only(top: Gap.lg),
            child: EmptyState(
              title: l10n.pantryNoResults,
              message: l10n.pantryNoResultsBody,
              icon: AppIcons.filter,
              actionLabel: l10n.suggestionsFilterAll,
              onAction: () => setState(() => _filter = _QuickFilter.all),
            ),
          )
        else ...[
          // Featured #1 Spotlight Dish Card
          Padding(
            padding: const EdgeInsets.only(bottom: Gap.md),
            child: StaggeredReveal(
              index: 0,
              child: _FeaturedSuggestionTile(suggestion: filtered.first),
            ),
          ),
          // Compact horizontal recipe cards for #2+
          for (var i = 1; i < filtered.length; i++)
            Padding(
              padding: const EdgeInsets.only(bottom: Gap.sm + 2),
              child: StaggeredReveal(
                index: i,
                child: _CompactSuggestionCard(suggestion: filtered[i]),
              ),
            ),
        ],
      ],
    );
  }
}

class _InlineDisclaimer extends StatelessWidget {
  const _InlineDisclaimer();

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(top: 1.5),
          child: Icon(AppIcons.info, size: 13.5, color: sweep.textTertiary),
        ),
        const SizedBox(width: 6),
        Expanded(
          child: Text(
            context.l10n.nutritionDisclaimer,
            style: context.text.labelSmall?.copyWith(
              letterSpacing: 0,
              color: sweep.textTertiary,
              height: 1.35,
            ),
          ),
        ),
      ],
    );
  }
}

class _FeaturedSuggestionTile extends StatelessWidget {
  const _FeaturedSuggestionTile({required this.suggestion});

  final DishSuggestion suggestion;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return SuggestionCard(
      title: suggestion.dish.name,
      score: suggestion.score,
      rank: suggestion.rank,
      meta: suggestion.dish.shortMeta(l10n),
      chips: suggestion.cardChips(l10n),
      fitReasons: suggestion.fitReasons.take(3).toList(),
      imageUrl: suggestion.dish.imageUrl,
      heroTag: 'dish-${suggestion.id}',
      onScoreTap: () => ScoreBreakdownSheet.show(context, suggestion),
      onTap: () => context.push(
        '${Routes.suggestions}/dish/${suggestion.id}',
        extra: suggestion,
      ),
    );
  }
}

/// Format 1 compact horizontal card for ranked dishes #2+.
class _CompactSuggestionCard extends StatelessWidget {
  const _CompactSuggestionCard({required this.suggestion});

  final DishSuggestion suggestion;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final chips = suggestion.cardChips(l10n);
    final primaryChip = chips.isNotEmpty ? chips.first : null;
    final topReason = suggestion.fitReasons.isNotEmpty
        ? suggestion.fitReasons.first
        : null;

    return TactileCard(
      color: cs.surfaceContainerLowest,
      borderColor: sweep.hairline,
      boxShadow: Shadows.e1,
      padding: const EdgeInsets.all(Gap.sm + 2),
      onTap: () => context.push(
        '${Routes.suggestions}/dish/${suggestion.id}',
        extra: suggestion,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Left rounded photo thumbnail + rank badge
          ClipRRect(
            borderRadius: Radii.brMd,
            child: SizedBox(
              width: 86,
              height: 86,
              child: Stack(
                children: [
                  Positioned.fill(
                    child: RecipeImage(
                      imageUrl: suggestion.dish.imageUrl,
                      heroTag: 'dish-${suggestion.id}',
                      fit: BoxFit.cover,
                      iconSize: 28,
                    ),
                  ),
                  Positioned(
                    top: 6,
                    left: 6,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 7,
                        vertical: 2.5,
                      ),
                      decoration: BoxDecoration(
                        color: cs.surfaceContainerLowest.withValues(
                          alpha: 0.94,
                        ),
                        borderRadius: BorderRadius.circular(Radii.pill),
                      ),
                      child: Text(
                        '#${suggestion.rank}',
                        style: AppTypography.tabular(
                          context.text.labelSmall?.copyWith(
                            color: cs.primary,
                            fontWeight: FontWeight.w800,
                            fontSize: 10.5,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: Gap.sm + 2),
          // Right details column
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  suggestion.dish.name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: context.text.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                    height: 1.25,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  suggestion.dish.shortMeta(l10n),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: context.text.bodySmall?.copyWith(
                    color: sweep.textTertiary,
                  ),
                ),
                if (topReason != null) ...[
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(AppIcons.checkCircle, size: 12.5, color: cs.primary),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          topReason,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: context.text.labelSmall?.copyWith(
                            letterSpacing: 0,
                            color: sweep.textSecondary,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
                const SizedBox(height: 8),
                Row(
                  children: [
                    if (primaryChip != null)
                      Expanded(
                        child: Align(
                          alignment: Alignment.centerLeft,
                          child: _MiniToneChip(chip: primaryChip),
                        ),
                      )
                    else
                      const Spacer(),
                    const SizedBox(width: Gap.xs),
                    InkWell(
                      borderRadius: BorderRadius.circular(Radii.pill),
                      onTap: () {
                        AppHaptics.selection();
                        ScoreBreakdownSheet.show(context, suggestion);
                      },
                      child: Padding(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 3,
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              '${suggestion.score} điểm',
                              style: AppTypography.tabular(
                                context.text.labelSmall?.copyWith(
                                  letterSpacing: 0,
                                  color: cs.primary,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                            ),
                            const SizedBox(width: 3),
                            Icon(AppIcons.info, size: 12.5, color: cs.primary),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MiniToneChip extends StatelessWidget {
  const _MiniToneChip({required this.chip});

  final SuggestionChip chip;

  @override
  Widget build(BuildContext context) {
    final (bg, fg) = switch (chip.tone) {
      SuggestionChipTone.nearExpiry => (
        context.sweep.culinaryAccentBg,
        context.sweep.onCulinaryAccentBg,
      ),
      SuggestionChipTone.available => (
        context.colors.primaryContainer,
        context.colors.onPrimaryContainer,
      ),
      SuggestionChipTone.toBuy => (
        context.sweep.subtleFill,
        context.sweep.textSecondary,
      ),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(Radii.pill),
      ),
      child: Text(
        chip.label,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: context.text.labelSmall?.copyWith(
          letterSpacing: 0,
          color: fg,
          fontWeight: FontWeight.w600,
          fontSize: 10.5,
        ),
      ),
    );
  }
}

class _AiStatusBanner extends ConsumerWidget {
  const _AiStatusBanner({required this.health});

  final AsyncValue<AiServiceHealthDto> health;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sweep = context.sweep;
    final color = context.colors.error;
    return Padding(
      padding: const EdgeInsets.fromLTRB(Gap.lg, 0, Gap.lg, Gap.sm),
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.sm,
          vertical: Gap.xs,
        ),
        decoration: BoxDecoration(
          color: sweep.expired.bg,
          borderRadius: Radii.brMd,
          border: Border.all(color: color.withValues(alpha: 0.25)),
        ),
        child: Row(
          children: [
            Icon(AppIcons.warning, size: 16, color: color),
            const SizedBox(width: Gap.xs),
            Expanded(
              child: Text(
                'Dịch vụ gợi ý tạm thời chưa kết nối',
                style: context.text.labelMedium?.copyWith(color: color),
              ),
            ),
            IconButton(
              visualDensity: VisualDensity.compact,
              tooltip: 'Thử lại',
              onPressed: () => ref.invalidate(aiServiceHealthProvider),
              icon: Icon(AppIcons.refresh, size: 16, color: color),
            ),
          ],
        ),
      ),
    );
  }
}
