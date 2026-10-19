import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/freshness_preview_sheet.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

class _MockApiClient extends Mock implements ApiClient {}

Map<String, dynamic> _questions() => {
  'kb_version': '0.3.0',
  'freshcheck_ingredient_id': 'rau_muong',
  'archetype_id': 'leafy',
  'questions': [
    {
      'axis': 'appearance',
      'question_vi': 'Lá có còn tươi không?',
      'options': [
        {'value': 'fresh', 'label_vi': 'Tươi'},
        {'value': 'wilted', 'label_vi': 'Héo'},
      ],
      'default': 'fresh',
    },
  ],
};

Map<String, dynamic> _preview({required bool blocked}) => {
  'blocked': blocked,
  'tier': blocked ? 'tier_4_spoiled' : 'tier_1_fresh',
  'remaining_days_min': blocked ? null : 3,
  'remaining_days_max': blocked ? null : 3,
  'reasons_vi': blocked ? ['Có dấu hiệu hỏng'] : <String>[],
  'storage_tips_vi': <String>[],
  'expires_at': blocked ? '2026-09-01T00:00:00Z' : '2026-09-04T00:00:00Z',
};

/// Opens the sheet; the returned notifier receives the accepted estimate.
Future<ValueNotifier<FreshnessEstimate?>> _open(
  WidgetTester tester,
  _MockApiClient api,
) async {
  final accepted = ValueNotifier<FreshnessEstimate?>(null);
  await tester.pumpWidget(
    ProviderScope(
      overrides: [apiClientProvider.overrideWithValue(api)],
      child: MaterialApp(
        locale: const Locale('vi'),
        supportedLocales: AppL10n.supportedLocales,
        localizationsDelegates: AppL10n.localizationsDelegates,
        theme: AppTheme.light,
        home: Builder(
          builder: (context) => Scaffold(
            body: TextButton(
              onPressed: () async {
                accepted.value = await FreshnessPreviewSheet.show(
                  context,
                  masterIngredientId: 'ing-1',
                  itemName: 'Rau muống',
                  storageTier: StorageTier.fridge,
                );
              },
              child: const Text('open'),
            ),
          ),
        ),
      ),
    ),
  );
  await tester.tap(find.text('open'));
  await tester.pumpAndSettle();
  return accepted;
}

void main() {
  late _MockApiClient api;

  setUp(() {
    api = _MockApiClient();
    when(
      () => api.get(ApiPaths.freshnessQuestions, query: any(named: 'query')),
    ).thenAnswer((_) async => _questions());
  });

  testWidgets('previews the expiry and returns the accepted answers', (
    tester,
  ) async {
    when(
      () => api.post(ApiPaths.freshnessPreview, body: any(named: 'body')),
    ).thenAnswer((_) async => _preview(blocked: false));

    final accepted = await _open(tester, api);
    await tester.tap(find.text('Héo'));
    await tester.pump();
    await tester.tap(find.text('Xem hạn ước tính'));
    await tester.pumpAndSettle();

    expect(find.textContaining('Hạn ước tính: 04/09/2026'), findsOneWidget);
    final sent =
        verify(
              () => api.post(
                ApiPaths.freshnessPreview,
                body: captureAny(named: 'body'),
              ),
            ).captured.single
            as Map<String, dynamic>;
    expect(sent['master_ingredient_id'], 'ing-1');
    expect(sent['storage_mode'], 'REFRIGERATED');
    expect(sent['answers'], {'appearance': 'wilted'});

    await tester.tap(find.text('Dùng hạn này (04/09/2026)'));
    await tester.pumpAndSettle();

    expect(find.byType(FreshnessPreviewSheet), findsNothing);
    expect(accepted.value?.answers, {'appearance': 'wilted'});
    expect(accepted.value?.expiresAt.toUtc(), DateTime.utc(2026, 9, 4));
  });

  testWidgets('a hard-stop result cannot be accepted as an expiry', (
    tester,
  ) async {
    when(
      () => api.post(ApiPaths.freshnessPreview, body: any(named: 'body')),
    ).thenAnswer((_) async => _preview(blocked: true));

    final accepted = await _open(tester, api);
    await tester.tap(find.text('Xem hạn ước tính'));
    await tester.pumpAndSettle();

    expect(find.text('Không nên sử dụng'), findsOneWidget);
    expect(find.textContaining('Dùng hạn này'), findsNothing);
    expect(find.text('Tính lại'), findsOneWidget);
    expect(accepted.value, isNull);
  });
}
