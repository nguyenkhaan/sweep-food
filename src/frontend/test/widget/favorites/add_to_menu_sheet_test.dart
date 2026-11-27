import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_menu.dart';
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_menus_controller.dart';
import 'package:sweepfood/features/favorites/presentation/widgets/add_to_menu_sheet.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

class _ControlledMenusController extends FavoriteMenusController {
  _ControlledMenusController(this._completer);
  final Completer<List<FavoriteMenu>> _completer;

  @override
  Future<List<FavoriteMenu>> build() => _completer.future;
}

void main() {
  testWidgets(
    'AddToMenuSheet renders cleanly in loading and loaded states without unbounded height error',
    (tester) async {
      final completer = Completer<List<FavoriteMenu>>();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            favoriteMenusControllerProvider.overrideWith(
              () => _ControlledMenusController(completer),
            ),
          ],
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            home: Scaffold(
              body: Builder(
                builder: (ctx) => Center(
                  child: FilledButton(
                    onPressed: () => AddToMenuSheet.show(
                      ctx,
                      recipeId: 'r-1',
                      recipeName: 'Cá hố kho cà chua',
                    ),
                    child: const Text('Open'),
                  ),
                ),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));

      // While loading: sheet renders cleanly with zero layout errors.
      expect(tester.takeException(), isNull);
      expect(find.text('Lưu vào thực đơn mẫu'), findsOneWidget);
      expect(find.text('Tạo thực đơn mới'), findsOneWidget);

      // Once loaded: menus appear cleanly.
      completer.complete([
        FavoriteMenu(
          id: 'm-1',
          name: 'Bữa cơm gia đình',
          description: 'Món ngon mỗi ngày',
          createdAt: DateTime(2026, 11, 27),
          updatedAt: DateTime(2026, 11, 27),
        ),
      ]);
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(find.text('Bữa cơm gia đình'), findsOneWidget);
    },
  );
}
