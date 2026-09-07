import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
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
      builder: (_) => AddToMenuSheet(
        recipeId: recipeId,
        recipeName: recipeName,
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final menusAsync = ref.watch(favoriteMenusControllerProvider);

    return SheetBody(
      title: 'Lưu vào thực đơn mẫu',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          OutlinedButton.icon(
            onPressed: () async {
              final result = await CreateEditMenuDialog.show(context);
              if (result != null) {
                try {
                  final newMenu = await ref
                      .read(favoriteMenusControllerProvider.notifier)
                      .createMenu(name: result.name, description: result.description);
                  await ref
                      .read(favoriteMenuDetailControllerProvider(newMenu.id).notifier)
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
            icon: const Icon(Icons.add_rounded),
            label: const Text('Tạo thực đơn mới'),
          ),
          Gap.gapMd,
          AsyncValueWidget<List<FavoriteMenu>>(
            value: menusAsync,
            onRetry: () => ref.invalidate(favoriteMenusControllerProvider),
            data: (menus) {
              if (menus.isEmpty) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: Gap.lg),
                  child: Center(
                    child: Text(
                      'Chưa có thực đơn nào. Bấm nút trên để tạo mới!',
                      style: context.text.bodyMedium?.copyWith(
                        color: context.sweep.textTertiary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                );
              }
              return Column(
                children: [
                  for (final menu in menus)
                    ListTile(
                      leading: Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: context.colors.primaryContainer,
                          borderRadius: Radii.brMd,
                        ),
                        child: Icon(
                          Icons.menu_book_rounded,
                          color: context.colors.onPrimaryContainer,
                          size: 20,
                        ),
                      ),
                      title: Text(menu.name, style: context.text.titleSmall),
                      subtitle: menu.description != null && menu.description!.isNotEmpty
                          ? Text(
                              menu.description!,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: context.text.bodySmall?.copyWith(
                                color: context.sweep.textTertiary,
                              ),
                            )
                          : null,
                      trailing: const Icon(Icons.add_circle_outline_rounded),
                      onTap: () async {
                        try {
                          await ref
                              .read(favoriteMenuDetailControllerProvider(menu.id).notifier)
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
                    ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}
