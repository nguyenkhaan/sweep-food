import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/features/ingest/presentation/screens/voice_review_screen.dart';
import 'package:frontend/l10n/app_localizations.dart';

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
}
