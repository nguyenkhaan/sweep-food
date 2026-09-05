import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/suggestions/presentation/screens/suggestion_list_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

void main() {
  testWidgets('RecipePromptBar toggles via AI button and filters suggestions', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const SuggestionListScreen(),
        ),
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));

    expect(find.text('Salad bơ ức gà'), findsOneWidget);
    expect(find.text('Canh chua cá lóc'), findsOneWidget);

    // Prompt box is hidden initially
    expect(find.byType(TextField), findsNothing);

    // Find AI button by tooltip or icon in AppBar actions
    final aiBtnFinder = find.byTooltip('AI Gợi ý prompt');
    expect(aiBtnFinder, findsOneWidget);

    // Tap AI button in AppBar to open prompt box
    await tester.tap(aiBtnFinder);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.byType(TextField), findsOneWidget);

    // Enter prompt canh
    await tester.enterText(find.byType(TextField), 'canh');
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));

    expect(find.text('Canh chua cá lóc'), findsOneWidget);
    expect(find.text('Salad bơ ức gà'), findsNothing);

    // Clear prompt using clear button
    await tester.tap(find.byIcon(Icons.clear_rounded));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));

    expect(find.text('Salad bơ ức gà'), findsOneWidget);

    // Tap quick prompt chip Món canh
    await tester.tap(find.text('Món canh'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));

    expect(find.text('Canh chua cá lóc'), findsOneWidget);
    expect(find.text('Salad bơ ức gà'), findsNothing);
  });
}
