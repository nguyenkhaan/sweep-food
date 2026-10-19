import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';
import 'package:sweepfood/features/ingest/presentation/screens/receipt_review_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

import '../../helpers/ingest_fixtures.dart';

void main() {
  testWidgets(
    'ReceiptReviewScreen renders parsed items list and selection actions',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(1000, 2400));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            home: ReceiptReviewScreen(job: receiptScanJob()),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Hóa đơn — 6 mục'), findsOneWidget);
      expect(find.text('Bách Hóa Xanh · 05/09'), findsOneWidget);
      expect(find.text('Cà chua bi'), findsOneWidget);
      expect(find.text('Trứng gà'), findsOneWidget);
      expect(find.text('Thịt ba chỉ'), findsOneWidget);
      expect(find.text('Thêm 6 mục vào kho'), findsOneWidget);

      await tester.tap(find.text('Bỏ chọn tất cả'));
      await tester.pumpAndSettle();

      expect(find.text('Chọn ít nhất 1 mục'), findsOneWidget);
    },
  );

  testWidgets(
    'ReceiptReviewScreen shows a partial-result recovery flow when no items were extracted',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(1000, 1800));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            home: const ReceiptReviewScreen(
              job: ScanJob(
                id: 'partial-receipt',
                type: ScanType.receipt,
                rawText: 'HOA DON BAN HANG',
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Chưa tách được nguyên liệu'), findsOneWidget);
      expect(find.text('Nội dung AI đọc được'), findsOneWidget);
      expect(find.text('HOA DON BAN HANG'), findsOneWidget);
      expect(find.text('Nhập tay'), findsOneWidget);
      expect(find.text('Chụp lại'), findsWidgets);
      expect(find.text('Chọn ít nhất 1 mục'), findsNothing);
    },
  );
}
