// Regression: the 5 StatefulShellRoute branches stay mounted in one IndexedStack
// subtree, so two default-tagged FloatingActionButtons (Pantry + Shopping) throw
// "multiple heroes share the same tag" on any route transition. Each shell FAB
// must carry a unique heroTag.
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/pantry/presentation/screens/pantry_screen.dart';
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
