import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/widgets/loading_skeleton.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';

/// Placeholder for recipe matching while the pantry recommendation flow is
/// being connected to its data source.
///
/// The previous implementation rendered a recipe catalogue declared directly
/// in this screen. Keeping the loading state here avoids presenting fabricated
/// recipe matches as real results.
class CookableRecipesScreen extends StatelessWidget {
  const CookableRecipesScreen({
    required this.selectedItems,
    this.initialPrompt = '',
    super.key,
  });

  final List<PantryItem> selectedItems;
  final String initialPrompt;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Công thức có thể nấu')),
      body: const _CookableRecipesSkeleton(),
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
      padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.sm, Gap.lg, Gap.xl),
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
