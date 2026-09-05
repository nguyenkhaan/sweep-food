import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/cooking/presentation/widgets/post_cook_confirm_sheet.dart';
import 'package:sweepfood/features/dishes/presentation/screens/dish_detail_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

void main() {
  testWidgets('DishDetailScreen direct cook skips PostCookConfirmSheet and confirms immediately', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1200, 2000));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const DishDetailScreen(dishId: 'd1'),
        ),
      ),
    );
    // Wait for recipe to load
    for (var i = 0; i < 5; i++) {
      await tester.pump(const Duration(milliseconds: 300));
    }

    expect(find.text('Salad bơ ức gà'), findsWidgets);
    expect(find.text('Đã nấu món này'), findsOneWidget);

    // Tap "Đã nấu món này". The direct-cook flow now chains several
    // sequential mock round trips (resolve/create today's meal-plan item,
    // preview, create session, complete) before the snackbar appears.
    await tester.tap(find.text('Đã nấu món này'));
    await tester.pump();
    for (var i = 0; i < 20; i++) {
      await tester.pump(const Duration(milliseconds: 300));
    }

    // Must NOT show PostCookConfirmSheet
    expect(find.byType(PostCookConfirmSheet), findsNothing);

    // Must show success snackbar
    expect(
      find.textContaining('Đã ghi nhận nấu Salad bơ ức gà!'),
      findsOneWidget,
    );
  });
}
