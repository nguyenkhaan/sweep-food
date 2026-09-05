// Regression: the 5 StatefulShellRoute branches stay mounted in one IndexedStack
// subtree, so two default-tagged FloatingActionButtons (Pantry + Shopping) throw
// "multiple heroes share the same tag" on any route transition. Each shell FAB
// must carry a unique heroTag.
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/pantry/presentation/screens/pantry_screen.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:sweepfood/features/shopping_list/presentation/controllers/shopping_list_controller.dart';
import 'package:sweepfood/features/shopping_list/presentation/screens/shopping_list_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

void main() {
  testWidgets('Pantry and Shopping FABs use distinct, non-null hero tags', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1200, 2000));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final tags = <Object?>[];
    for (final screen in const [PantryScreen(), ShoppingListScreen()]) {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            // The Shopping FAB only shows once a list has been generated —
            // stub one so this test can focus on the hero-tag invariant.
            shoppingListControllerProvider.overrideWith(
              () => _FakeShoppingListController(),
            ),
          ],
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            home: screen,
          ),
        ),
      );
      // Past the mock's ~320ms latency; Shopping only shows its FAB once loaded.
      for (var i = 0; i < 8; i++) {
        await tester.pump(const Duration(milliseconds: 300));
      }
      final fab = tester.widget<FloatingActionButton>(
        find.byType(FloatingActionButton),
      );
      tags.add(fab.heroTag);
    }

    expect(tags[0], isNotNull);
    expect(tags[1], isNotNull);
    expect(tags[0], isNot(equals(tags[1])));
  });
}

class _FakeShoppingListController extends ShoppingListController {
  @override
  Future<ShoppingList?> build() async => const ShoppingList(
        id: 'sl1',
        items: [],
      );
}
