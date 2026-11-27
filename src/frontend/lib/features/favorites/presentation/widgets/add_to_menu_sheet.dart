import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/loading_skeleton.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_menu.dart';
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_menus_controller.dart';
import 'package:sweepfood/features/favorites/presentation/widgets/create_edit_menu_dialog.dart';

class AddToMenuSheet extends ConsumerWidget {
  const AddToMenuSheet({
    required this.recipeId,
    required this.recipeName,
    super.key,
  });

  final String recipeId;
  final String recipeName;

  static Future<void> show(
    BuildContext context, {
    required String recipeId,
    required String recipeName,
  }) {
    return showAppBottomSheet(
      context,
      builder: (_) =>
          AddToMenuSheet(recipeId: recipeId, recipeName: recipeName),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final menusAsync = ref.watch(favoriteMenusControllerProvider);
    final cs = context.colors;
    final sweep = context.sweep;

    return SheetBody(
      icon: AppIcons.bookmark,
      title: 'Lưu vào thực đơn mẫu',
      subtitle: recipeName,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SheetCancelButton(
            icon: AppIcons.add,
            label: 'Tạo thực đơn mới',
            onPressed: () async {
              final result = await CreateEditMenuDialog.show(context);
              if (result != null) {
                try {
                  final newMenu = await ref
                      .read(favoriteMenusControllerProvider.notifier)
                      .createMenu(
                        name: result.name,
                        description: result.description,
                      );
                  await ref
                      .read(
                        favoriteMenuDetailControllerProvider(
                          newMenu.id,
                        ).notifier,
                      )
                      .addRecipe(recipeId);
                  if (context.mounted) {
                    Navigator.of(context).pop();
                    AppSnack.show(
                      context,
                      'Đã thêm "$recipeName" vào thực đơn "${newMenu.name}"',
                    );
                  }
                } catch (e) {
                  if (context.mounted) {
                    AppSnack.show(context, 'Lỗi: $e');
                  }
                }
              }
            },
          ),
          Gap.gapMd,
          AsyncValueWidget<List<FavoriteMenu>>(
            value: menusAsync,
            onRetry: () => ref.invalidate(favoriteMenusControllerProvider),
            loading: const _MenusLoadingPlaceholder(),
            data: (menus) {
              if (menus.isEmpty) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: Gap.lg),
                  child: Center(
                    child: Text(
                      'Chưa có thực đơn nào. Bấm nút trên để tạo mới!',
                      style: context.text.bodyMedium?.copyWith(
                        color: sweep.textTertiary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                );
              }
              return ConstrainedBox(
                constraints: BoxConstraints(
                  maxHeight: MediaQuery.sizeOf(context).height * 0.45,
                ),
                child: SingleChildScrollView(
                  child: SheetGroupCard(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        for (var i = 0; i < menus.length; i++) ...[
                          if (i > 0) Divider(height: 1, color: sweep.hairline),
                          InkWell(
                            onTap: () async {
                              AppHaptics.selection();
                              final menu = menus[i];
                              try {
                                await ref
                                    .read(
                                      favoriteMenuDetailControllerProvider(
                                        menu.id,
                                      ).notifier,
                                    )
                                    .addRecipe(recipeId);
                                if (context.mounted) {
                                  Navigator.of(context).pop();
                                  AppSnack.show(
                                    context,
                                    'Đã thêm "$recipeName" vào thực đơn "${menu.name}"',
                                  );
                                }
                              } catch (e) {
                                if (context.mounted) {
                                  AppSnack.show(context, 'Lỗi: $e');
                                }
                              }
                            },
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: Gap.md,
                                vertical: Gap.sm + 4,
                              ),
                              child: Row(
                                children: [
                                  Container(
                                    width: 38,
                                    height: 38,
                                    decoration: BoxDecoration(
                                      color: cs.primaryContainer,
                                      borderRadius: Radii.brMd,
                                    ),
                                    child: Icon(
                                      AppIcons.bookOpen,
                                      color: cs.primary,
                                      size: 18,
                                    ),
                                  ),
                                  const SizedBox(width: Gap.sm + 2),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          menus[i].name,
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                          style: context.text.titleSmall
                                              ?.copyWith(
                                                fontWeight: FontWeight.w700,
                                              ),
                                        ),
                                        if (menus[i].description != null &&
                                            menus[i]
                                                .description!
                                                .isNotEmpty) ...[
                                          const SizedBox(height: 2),
                                          Text(
                                            menus[i].description!,
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                            style: context.text.bodySmall
                                                ?.copyWith(
                                                  color: sweep.textSecondary,
                                                ),
                                          ),
                                        ],
                                      ],
                                    ),
                                  ),
                                  const SizedBox(width: Gap.xs),
                                  Icon(
                                    AppIcons.add,
                                    size: 18,
                                    color: cs.primary,
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

/// Bounded skeleton placeholder so [AddToMenuSheet] never mounts an unbounded
/// `ListView` inside a shrink-wrapped bottom sheet `Column`.
class _MenusLoadingPlaceholder extends StatelessWidget {
  const _MenusLoadingPlaceholder();

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return SheetGroupCard(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          for (var i = 0; i < 2; i++) ...[
            if (i > 0) Divider(height: 1, color: sweep.hairline),
            const Padding(
              padding: EdgeInsets.symmetric(
                horizontal: Gap.md,
                vertical: Gap.sm + 4,
              ),
              child: Row(
                children: [
                  SkeletonBox(width: 38, height: 38, radius: Radii.md),
                  SizedBox(width: Gap.sm + 2),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SkeletonBox(width: 140, height: 14),
                        SizedBox(height: 6),
                        SkeletonBox(width: 96, height: 11),
                      ],
                    ),
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
