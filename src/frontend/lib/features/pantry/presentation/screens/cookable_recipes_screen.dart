import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/core/widgets/loading_skeleton.dart';
import 'package:sweepfood/core/widgets/suggestion_card.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';
import 'package:sweepfood/features/suggestions/presentation/widgets/suggestion_card_chips.dart';

/// Real recommendations for the pantry items selected by the user (Concept B · Format 1).
class CookableRecipesScreen extends ConsumerWidget {
  const CookableRecipesScreen({
    required this.selectedItems,
    this.initialPrompt = '',
    super.key,
  });

  final List<PantryItem> selectedItems;
  final String initialPrompt;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final query = (items: selectedItems, prompt: initialPrompt);
    final suggestions = ref.watch(cookableSuggestionProvider(query));
    final cs = context.colors;

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: 'Công thức có thể nấu',
              subtitle: selectedItems.isNotEmpty
                  ? 'Từ ${selectedItems.length} nguyên liệu đã chọn'
                  : null,
            ),
            Expanded(
              child: RefreshIndicator(
                onRefresh: () =>
                    ref.refresh(cookableSuggestionProvider(query).future),
                child: AsyncValueWidget<List<DishSuggestion>>(
                  value: suggestions,
                  loading: const _CookableRecipesSkeleton(),
                  onRetry: () =>
                      ref.invalidate(cookableSuggestionProvider(query)),
                  data: (items) => _CookableRecipeList(items: items),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CookableRecipeList extends StatelessWidget {
  const _CookableRecipeList({required this.items});

  final List<DishSuggestion> items;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return ListView(
        key: const Key('cookable-recipes-empty'),
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xl, Gap.lg, Gap.xxl),
        children: [
          EmptyState(
            illustrationAsset: 'assets/illustrations/empty_search.svg',
            title: 'Chưa có công thức phù hợp',
            message: 'Hãy thử chọn thêm nguyên liệu hoặc thay đổi yêu cầu.',
            icon: AppIcons.utensils,
            actionLabel: 'Quay lại chọn nguyên liệu',
            onAction: () => context.pop(),
          ),
        ],
      );
    }

    return ListView.builder(
      key: const Key('cookable-recipes-results'),
      padding: EdgeInsets.fromLTRB(
        Gap.lg,
        Gap.xs,
        Gap.lg,
        MediaQuery.paddingOf(context).bottom + Gap.xl,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final suggestion = items[index];
        return Padding(
          padding: const EdgeInsets.only(bottom: Gap.md),
          child: SuggestionCard(
            title: suggestion.dish.name,
            score: suggestion.score,
            rank: suggestion.rank,
            meta: suggestion.dish.shortMeta(context.l10n),
            chips: suggestion.cardChips(context.l10n),
            fitReasons: suggestion.fitReasons.take(3).toList(),
            imageUrl: suggestion.dish.imageUrl,
            heroTag: 'dish-${suggestion.id}',
            onTap: () => context.push(
              '${Routes.suggestions}/dish/${suggestion.id}',
              extra: suggestion,
            ),
          ),
        );
      },
    );
  }
}

class _CookableRecipesSkeleton extends StatelessWidget {
  const _CookableRecipesSkeleton();

  static const _cardCount = 4;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      key: const Key('cookable-recipes-skeleton'),
      padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xl),
      itemCount: _cardCount,
      separatorBuilder: (_, __) => const SizedBox(height: Gap.md),
      itemBuilder: (_, __) => const _RecipeCardSkeleton(),
    );
  }
}

class _RecipeCardSkeleton extends StatelessWidget {
  const _RecipeCardSkeleton();

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(Gap.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                SkeletonBox(width: 44, height: 44, radius: Radii.md),
                SizedBox(width: Gap.sm),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SkeletonBox(width: 180, height: 18),
                      SizedBox(height: Gap.xs),
                      SkeletonBox(width: 128, height: 12),
                    ],
                  ),
                ),
                SkeletonBox(width: 72, height: 24, radius: Radii.pill),
              ],
            ),
            SizedBox(height: Gap.md),
            SkeletonBox(height: 12),
            SizedBox(height: Gap.xs),
            SkeletonBox(width: 220, height: 12),
            SizedBox(height: Gap.md),
            SkeletonBox(height: 40, radius: Radii.md),
          ],
        ),
      ),
    );
  }
}
