import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';
import 'package:sweepfood/features/ingest/presentation/screens/label_review_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

import '../../helpers/ingest_fixtures.dart';

void main() {
  testWidgets(
    'LabelReviewScreen renders OCR parsed fields and warning badges',
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
            home: LabelReviewScreen(job: labelScanJob()),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Kiểm tra thông tin'), findsOneWidget);
      expect(find.text('Cà chua bi'), findsOneWidget);
      expect(find.text('500 g'), findsOneWidget);
      expect(find.text('Hạn: 10/09/2026'), findsOneWidget);
      expect(find.textContaining('hãy kiểm tra lại'), findsOneWidget);
      expect(find.text('Tầng bảo quản'), findsOneWidget);
      expect(find.text('Thêm vào kho'), findsOneWidget);
    },
  );

  testWidgets(
    'LabelReviewScreen labels mock barcode context clearly',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(1000, 2400));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      const barcodeJob = ScanJob(
        id: 'job_barcode_001',
        type: ScanType.label,
        fieldCount: 2,
        rawText: '__MOCK_BARCODE__',
        items: [ParsedItemDraft(name: 'Sữa tươi', quantity: 1)],
      );

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            home: const LabelReviewScreen(job: barcodeJob),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Ảnh mã vạch'), findsOneWidget);
      expect(find.text('Ảnh tem nhãn'), findsNothing);
      expect(find.textContaining('dữ liệu thử nghiệm'), findsOneWidget);
      expect(find.byIcon(Icons.qr_code_2_rounded), findsOneWidget);
    },
  );
}
