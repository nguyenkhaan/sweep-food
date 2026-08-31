// H-01 Home Dashboard: renders the dashboard from the mock fixtures, and shows
// the "add your first ingredient" CTA when the pantry is empty (spec M2).
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/core/widgets/suggestion_card.dart';
import 'package:frontend/features/home/presentation/controllers/home_controller.dart';
import 'package:frontend/features/home/presentation/screens/home_screen.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_summary.dart';

Future<void> _settle(WidgetTester tester) async {
  // Past the mock's ~320ms latency per hop (summary + list + suggestions).
  // Avoid pumpAndSettle — the loading skeleton animates forever.
  await tester.pump();
  for (var i = 0; i < 8; i++) {
    await tester.pump(const Duration(milliseconds: 300));
  }
}

void main() {
  testWidgets('renders the dashboard from the fixtures with wired suggestions', (
    tester,
  ) async {
    // Tall surface so the whole lazy ListView builds without scrolling.
    await tester.binding.setSurfaceSize(const Size(1000, 2800));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(theme: AppTheme.light, home: const HomeScreen()),
      ),
    );
    await _settle(tester);

    expect(find.textContaining('Chào buổi'), findsOneWidget);
    expect(find.text('Hôm nay ăn gì?'), findsOneWidget);
    // Grid tile count comes from the real S-01 list (suggestions.json has 4).
    expect(find.text('4 món phù hợp'), findsOneWidget);
    // SectionHeader upper-cases its title.
    expect(find.text('GỢI Ý CHO BẠN'), findsOneWidget);
    // The preview is wired to suggestions.json (was hard-coded before)…
    expect(find.text('Salad bơ ức gà'), findsOneWidget);
    expect(find.text('Canh chua cá lóc'), findsOneWidget);
    // …and every preview card is now tappable (was inert before).
    final cards = tester.widgetList<SuggestionCard>(find.byType(SuggestionCard));
    expect(cards, isNotEmpty);
    expect(cards.every((c) => c.onTap != null), isTrue);
  });

  testWidgets('shows the add-first-ingredient CTA when the pantry is empty', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          homeDashboardProvider.overrideWith(
            (ref) async => const HomeDashboardData(
              summary: PantrySummary(
                totalCount: 0,
                countByTier: {},
                nearExpiry: [],
                wasteReductionCount: 0,
              ),
              nearExpiryItems: [],
              suggestions: [],
              suggestionCount: 0,
            ),
          ),
        ],
        child: MaterialApp(theme: AppTheme.light, home: const HomeScreen()),
      ),
    );
    // Drain the notification-badge fetch (mock latency) so no timer leaks.
    await _settle(tester);

    expect(find.text('Kho của bạn đang trống'), findsOneWidget);
    expect(find.text('Thêm nguyên liệu đầu tiên'), findsOneWidget);
    // None of the full-dashboard sections render.
    expect(find.text('GỢI Ý CHO BẠN'), findsNothing);
    expect(find.text('Kho thực phẩm'), findsNothing);
  });
}
