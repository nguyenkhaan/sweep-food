// Smoke test: S-01 renders the ranked list from the mock fixture, and the
// score-breakdown sheet (S-02) opens.
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/features/suggestions/presentation/screens/suggestion_list_screen.dart';

void main() {
  testWidgets('renders ranked cards and opens the score-breakdown sheet', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.light,
          home: const SuggestionListScreen(),
        ),
      ),
    );
    // Past the mock's ~320ms latency (avoid pumpAndSettle — skeleton animates).
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));

    expect(find.text('Salad bơ ức gà'), findsOneWidget);
    expect(find.text('Canh chua cá lóc'), findsOneWidget);
    expect(find.textContaining('món hợp nhất'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.help_outline_rounded).first);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.textContaining('Điểm = 0.4·E'), findsOneWidget);
    expect(find.textContaining('Dùng đồ cận hạn'), findsOneWidget);
  });
}
