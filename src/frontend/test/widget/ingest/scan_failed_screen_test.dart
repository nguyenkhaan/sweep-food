import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/features/ingest/presentation/screens/scan_failed_screen.dart';
import 'package:frontend/l10n/app_localizations.dart';

void main() {
  testWidgets(
    'ScanFailedScreen renders error title, reasons and action buttons',
    (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const ScanFailedScreen(),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Không đọc được nhãn'), findsOneWidget);
      expect(find.text('Ảnh bị mờ hoặc chụp nghiêng'), findsOneWidget);
      expect(find.text('Nhãn bị rách hoặc phai mực'), findsOneWidget);
      expect(find.text('Thiếu sáng khi chụp'), findsOneWidget);
      expect(find.text('Chụp lại'), findsOneWidget);
      expect(find.text('Nhập tay'), findsOneWidget);
    },
  );
}
