import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/features/pantry/presentation/screens/pantry_item_detail_screen.dart';
import 'package:frontend/l10n/app_localizations.dart';

Widget _app(String id) => ProviderScope(
  child: MaterialApp(
    locale: const Locale('vi'),
    supportedLocales: AppL10n.supportedLocales,
    localizationsDelegates: AppL10n.localizationsDelegates,
    theme: AppTheme.light,
    home: PantryItemDetailScreen(itemId: id),
  ),
);

Future<void> _settle(WidgetTester tester) async {
  await tester.pump();
  for (var i = 0; i < 8; i++) {
    await tester.pump(const Duration(milliseconds: 300));
  }
}

void main() {
  testWidgets('K-02 renders an item from the mock list without layout errors', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(400, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_app('p1'));
    await _settle(tester);

    expect(tester.takeException(), isNull);
    // p1 = "Cải bó xôi" in assets/mock/pantry_items.json
    expect(find.text('Cải bó xôi'), findsWidgets);
    expect(find.text('Chi tiết'), findsOneWidget);
    expect(find.text('Đã dùng hết'), findsOneWidget);
  });

  testWidgets('K-02 falls back to the not-found state for an unknown id', (
    tester,
  ) async {
    await tester.pumpWidget(_app('does-not-exist'));
    await _settle(tester);

    expect(tester.takeException(), isNull);
    expect(find.text('Không tìm thấy nguyên liệu'), findsOneWidget);
  });
}
