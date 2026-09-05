import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/screens/cookable_recipes_screen.dart';
import 'package:sweepfood/features/pantry/presentation/screens/pantry_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

void main() {
  testWidgets('PantryScreen supports multi-selection and navigates to CookableRecipesScreen', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1200, 2000));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final router = GoRouter(
      initialLocation: Routes.pantry,
      routes: [
        GoRoute(
          path: Routes.pantry,
          builder: (context, state) => const PantryScreen(),
          routes: [
            GoRoute(
              path: Routes.cookableRecipes,
              builder: (context, state) {
                final items = (state.extra as List<PantryItem>?) ?? [];
                return CookableRecipesScreen(selectedItems: items);
              },
            ),
          ],
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp.router(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          routerConfig: router,
        ),
      ),
    );
    // Wait for mock data
    for (var i = 0; i < 5; i++) {
      await tester.pump(const Duration(milliseconds: 300));
    }

    expect(find.text('Cải bó xôi'), findsOneWidget);
    expect(find.text('Cà chua bi'), findsOneWidget);

    // Initial state: no bottom bar
    expect(find.textContaining('Đã chọn'), findsNothing);

    // Select first item by tapping checkbox
    expect(find.byType(Checkbox), findsWidgets);
    await tester.tap(find.byType(Checkbox).first);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));

    // Bottom action bar appears
    expect(find.text('Đã chọn 1'), findsOneWidget);
    expect(find.text('Xem công thức'), findsOneWidget);

    // Select second item
    await tester.tap(find.byType(Checkbox).at(1));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('Đã chọn 2'), findsOneWidget);

    // Tap Xem công thức
    await tester.tap(find.text('Xem công thức'));
    await tester.pumpAndSettle();

    // CookableRecipesScreen opened
    expect(find.byType(CookableRecipesScreen), findsOneWidget);
    expect(find.text('Công thức có thể nấu'), findsOneWidget);

    // Back to PantryScreen
    router.pop();
    await tester.pumpAndSettle();

    // Tap Bỏ chọn
    await tester.tap(find.text('Bỏ chọn'));
    await tester.pump();

    expect(find.textContaining('Đã chọn'), findsNothing);
  });
}