import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/network/mock_api_client.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/features/favorites/presentation/screens/favorites_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

void main() {
  testWidgets('FavoritesScreen displays favorite recipes and menus tabs', (tester) async {
    final mockApi = MockApiClient();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          apiClientProvider.overrideWithValue(mockApi),
        ],
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const FavoritesScreen(),
        ),
      ),
    );

    // Initial pump + wait for mock latency
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));

    // Verify TabBar titles
    expect(find.text('Món yêu thích'), findsOneWidget);
    expect(find.text('Thực đơn mẫu'), findsOneWidget);

    // Recipe tab should show 'Canh chua cá lóc' from mockApi
    expect(find.text('Canh chua cá lóc'), findsOneWidget);

    // Switch to Menus tab
    await tester.tap(find.text('Thực đơn mẫu'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 1000));
    await tester.pump(const Duration(milliseconds: 500));

    // Menu tab should display menu from mockApi
    expect(find.text('Bữa cơm gia đình'), findsOneWidget);
  });
}
