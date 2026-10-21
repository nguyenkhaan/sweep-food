import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/pantry/data/models/freshness_dto.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/freshness_controller.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/expiry_freshness_row.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

const _questions = FreshnessQuestionsResponseDto(
  kbVersion: '0.3.0',
  freshcheckIngredientId: 'rau_muong',
  archetypeId: 'leafy',
  questions: [],
);

Future<void> _pump(
  WidgetTester tester, {
  String? masterIngredientId,
  DateTime? expiryDate,
  FreshnessEstimate? freshness,
  bool questionsFail = false,
  void Function(DateTime?, FreshnessEstimate?)? onChanged,
}) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        if (masterIngredientId != null)
          freshnessQuestionsProvider(masterIngredientId).overrideWith(
            (ref) async =>
                questionsFail ? throw Exception('MAPPING_UNAVAILABLE') : _questions,
          ),
      ],
      child: MaterialApp(
        locale: const Locale('vi'),
        supportedLocales: AppL10n.supportedLocales,
        localizationsDelegates: AppL10n.localizationsDelegates,
        theme: AppTheme.light,
        home: Scaffold(
          body: ExpiryFreshnessRow(
            itemName: 'Rau muống',
            storageTier: StorageTier.fridge,
            expiryDate: expiryDate,
            freshness: freshness,
            masterIngredientId: masterIngredientId,
            onChanged: onChanged ?? (_, _) {},
          ),
        ),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('without a catalog match only manual entry is offered', (
    tester,
  ) async {
    await _pump(tester);

    expect(find.text('Nhập hạn'), findsOneWidget);
    expect(find.text('Kiểm tra hạn nhanh'), findsNothing);
    expect(find.textContaining('Chưa có hạn'), findsOneWidget);
  });

  testWidgets('a matched, FreshCheck-supported item offers both options', (
    tester,
  ) async {
    await _pump(tester, masterIngredientId: 'ing-1');

    expect(find.text('Nhập hạn'), findsOneWidget);
    expect(find.text('Kiểm tra hạn nhanh'), findsOneWidget);
  });

  testWidgets('hides FreshCheck when the ingredient has no FreshCheck mapping', (
    tester,
  ) async {
    await _pump(tester, masterIngredientId: 'ing-1', questionsFail: true);

    expect(find.text('Nhập hạn'), findsOneWidget);
    expect(find.text('Kiểm tra hạn nhanh'), findsNothing);
  });

  testWidgets('a printed/read date is shown and can be cleared', (tester) async {
    (DateTime?, FreshnessEstimate?)? changed;
    await _pump(
      tester,
      masterIngredientId: 'ing-1',
      expiryDate: DateTime(2026, 9, 10),
      onChanged: (d, f) => changed = (d, f),
    );

    expect(find.text('Hạn: 10/09/2026'), findsOneWidget);
    expect(find.text('Kiểm tra hạn nhanh'), findsNothing);

    tester.widget<InputChip>(find.byType(InputChip)).onDeleted!();
    await tester.pump();

    expect(changed, (null, null));
  });

  testWidgets('an accepted FreshCheck estimate is summarised in days', (
    tester,
  ) async {
    await _pump(
      tester,
      masterIngredientId: 'ing-1',
      freshness: FreshnessEstimate(
        answers: const {'appearance': 'fresh'},
        expiresAt: DateTime(2026, 9, 3),
        remainingDaysMin: 2,
        remainingDaysMax: 4,
      ),
    );

    expect(find.textContaining('FreshCheck: còn 2–4 ngày'), findsOneWidget);
    expect(find.text('Nhập hạn'), findsNothing);
  });
}
