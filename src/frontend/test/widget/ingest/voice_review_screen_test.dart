import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';
import 'package:sweepfood/features/ingest/presentation/screens/voice_review_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

import '../../helpers/ingest_fixtures.dart';

void main() {
  testWidgets('VoiceReviewScreen renders transcript and parsed items list', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1000, 2400));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: VoiceReviewScreen(job: voiceScanJob()),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Kiểm tra kết quả'), findsOneWidget);
    expect(find.textContaining('2 lạng thịt bò'), findsOneWidget);
    expect(find.text('Ghi lại'), findsOneWidget);
    expect(find.text('Thịt bò'), findsOneWidget);
    expect(find.text('Cải bó xôi'), findsOneWidget);
    expect(find.text('Trứng gà'), findsOneWidget);
    expect(find.text('Thêm dòng'), findsOneWidget);
    expect(find.text('Thêm 3 nguyên liệu'), findsOneWidget);
  });

  testWidgets('warns when ASR likely omitted an item or misread quantity', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1000, 2400));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    const job = ScanJob(
      id: 'faulty-asr',
      type: ScanType.voice,
      rawText: '2 loại thịt bò, 1 bụng cải bó xuôi, 3 quả trứng',
      items: [
        ParsedItemDraft(name: 'Thịt bò', quantity: 2000),
        ParsedItemDraft(name: 'Trứng gà', quantity: 1),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const VoiceReviewScreen(job: job),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Cần kiểm tra lại kết quả'), findsOneWidget);
    expect(find.textContaining('Có thể thiếu 1 nguyên liệu'), findsOneWidget);
    expect(find.textContaining('Có số lượng bất thường'), findsOneWidget);
  });
}
