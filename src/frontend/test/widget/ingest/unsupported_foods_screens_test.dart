import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';
import 'package:sweepfood/features/ingest/presentation/screens/label_review_screen.dart';
import 'package:sweepfood/features/ingest/presentation/screens/receipt_review_screen.dart';
import 'package:sweepfood/features/ingest/presentation/screens/voice_review_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

import '../../helpers/ingest_fixtures.dart';

const _rowMessage = 'Thực phẩm này app chưa hỗ trợ, thử lại sau';
const _hint = 'Bỏ các thực phẩm chưa hỗ trợ để tiếp tục';
const _unknown = ParsedItemDraft(name: 'Món lạ', quantity: 100);

Future<void> _pump(WidgetTester tester, Widget screen) async {
  await tester.binding.setSurfaceSize(const Size(1000, 2600));
  addTearDown(() => tester.binding.setSurfaceSize(null));
  await tester.pumpWidget(
    ProviderScope(
      child: MaterialApp(
        locale: const Locale('vi'),
        supportedLocales: AppL10n.supportedLocales,
        localizationsDelegates: AppL10n.localizationsDelegates,
        theme: AppTheme.light,
        home: screen,
      ),
    ),
  );
  await tester.pumpAndSettle();
  // Recognized foods look up FreshCheck questions (a delayed mock call).
  await tester.pump(const Duration(seconds: 1));
}

ElevatedButton _button(WidgetTester tester, String label) =>
    tester.widget<ElevatedButton>(find.widgetWithText(ElevatedButton, label));

void main() {
  testWidgets('receipt: only the unsupported row is red, and ticking it blocks adding', (
    tester,
  ) async {
    await _pump(
      tester,
      ReceiptReviewScreen(
        job: ScanJob(
          id: 'r',
          type: ScanType.receipt,
          items: [...receiptScanJob().items, _unknown],
        ),
      ),
    );

    // One message, under the unrecognized food only; the other six are clean.
    expect(find.text(_rowMessage), findsOneWidget);
    // It starts unticked, so the supported six can be added right away.
    expect(find.text(_hint), findsNothing);
    expect(_button(tester, 'Thêm 6 mục vào kho').onPressed, isNotNull);

    // Ticking the unsupported food blocks the whole add and explains why.
    await tester.tap(find.text('Món lạ'));
    await tester.pumpAndSettle();
    expect(find.text(_hint), findsOneWidget);
    expect(_button(tester, 'Thêm 7 mục vào kho').onPressed, isNull);

    // Unticking it (or removing it) lets the rest through again.
    await tester.tap(find.text('Món lạ'));
    await tester.pumpAndSettle();
    expect(find.text(_hint), findsNothing);
    expect(_button(tester, 'Thêm 6 mục vào kho').onPressed, isNotNull);
  });

  testWidgets('receipt: a fully supported list shows no unsupported message', (
    tester,
  ) async {
    await _pump(tester, ReceiptReviewScreen(job: receiptScanJob()));

    expect(find.text(_rowMessage), findsNothing);
    expect(find.text(_hint), findsNothing);
    expect(_button(tester, 'Thêm 6 mục vào kho').onPressed, isNotNull);
  });

  testWidgets('voice: an unsupported row is red and the add stays blocked until it is removed', (
    tester,
  ) async {
    await _pump(
      tester,
      VoiceReviewScreen(
        job: ScanJob(
          id: 'v',
          type: ScanType.voice,
          rawText: 'thịt bò, cải bó xôi, trứng, món lạ',
          items: [...voiceScanJob().items, _unknown],
        ),
      ),
    );

    expect(find.text(_rowMessage), findsOneWidget);
    expect(find.text(_hint), findsOneWidget);
    expect(_button(tester, 'Thêm 4 nguyên liệu').onPressed, isNull);

    // Remove the unsupported food (its row has the last close icon).
    await tester.tap(find.byIcon(Icons.close_rounded).last);
    await tester.pumpAndSettle();

    expect(find.text(_rowMessage), findsNothing);
    expect(find.text(_hint), findsNothing);
    expect(_button(tester, 'Thêm 3 nguyên liệu').onPressed, isNotNull);
  });

  testWidgets('label: an unrecognized food shows the red message and disables saving', (
    tester,
  ) async {
    await _pump(
      tester,
      const LabelReviewScreen(
        job: ScanJob(id: 'l', type: ScanType.label, items: [_unknown]),
      ),
    );

    expect(find.text(_rowMessage), findsOneWidget);
    expect(_button(tester, 'Thêm vào kho').onPressed, isNull);
  });

  testWidgets('label: a recognized food has no message and can be saved', (
    tester,
  ) async {
    await _pump(tester, LabelReviewScreen(job: labelScanJob()));

    expect(find.text(_rowMessage), findsNothing);
    expect(_button(tester, 'Thêm vào kho').onPressed, isNotNull);
  });
}
