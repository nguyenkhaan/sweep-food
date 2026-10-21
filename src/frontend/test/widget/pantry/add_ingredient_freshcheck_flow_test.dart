import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/features/pantry/presentation/screens/add_ingredient_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

class _MockApiClient extends Mock implements ApiClient {}

/// Manual entry → smart parser → optional FreshCheck → save: the whole path
/// through the real screen, controller, repository and data sources, with only
/// the HTTP client faked.
void main() {
  testWidgets(
    'typed name is matched by the smart parser, FreshCheck supplies the expiry '
    'and is recorded through the assessment after the item is saved',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(1000, 2400));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      final api = _MockApiClient();

      when(
        () => api.get(ApiPaths.ingredients, query: any(named: 'query')),
      ).thenAnswer(
        (_) async => {
          'items': <Map<String, dynamic>>[],
          'total': 0,
          'page': 1,
          'per_page': 8,
        },
      );
      when(
        () => api.get(ApiPaths.inventoryBatches, query: any(named: 'query')),
      ).thenAnswer(
        (_) async => {
          'items': <Map<String, dynamic>>[],
          'total': 0,
          'page': 1,
          'per_page': 100,
        },
      );
      when(
        () => api.post(ApiPaths.extractionText, body: any(named: 'body')),
      ).thenAnswer(
        (_) async => {
          'request_id': 'r1',
          'status': 'PARTIAL',
          'provider': 'SWEEP_FOOD_AI',
          'raw_text': 'thịt ba rọi 500g',
          'fields': {
            'ingredient_name': 'Thịt ba chỉ',
            'raw_name': 'thịt ba rọi',
            'master_ingredient_id': 'ing-7',
            'quantity': 500.0,
            'unit': 'GRAM',
          },
          'confidence': <String, dynamic>{},
          'warnings': <String>[],
          'persisted': false,
        },
      );
      when(
        () => api.get(ApiPaths.freshnessQuestions, query: any(named: 'query')),
      ).thenAnswer(
        (_) async => {
          'kb_version': '0.3.0',
          'freshcheck_ingredient_id': 'thit_heo',
          'archetype_id': 'meat',
          'questions': [
            {
              'axis': 'smell',
              'question_vi': 'Mùi thịt thế nào?',
              'options': [
                {'value': 'fresh', 'label_vi': 'Bình thường'},
                {'value': 'off', 'label_vi': 'Hơi hôi'},
              ],
              'default': 'fresh',
            },
          ],
        },
      );
      when(
        () => api.post(ApiPaths.freshnessPreview, body: any(named: 'body')),
      ).thenAnswer(
        (_) async => {
          'blocked': false,
          'tier': 'tier_1_fresh',
          'remaining_days_min': 2,
          'remaining_days_max': 3,
          'reasons_vi': <String>[],
          'storage_tips_vi': <String>[],
          'expires_at': '2030-01-04T00:00:00Z',
        },
      );
      when(
        () => api.post(
          ApiPaths.inventoryBatches,
          body: any(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).thenAnswer(
        (_) async => {
          'id': 'batch-1',
          'master_ingredient_id': 'ing-7',
          'ingredient_name': 'Thịt ba chỉ',
          'current_quantity': 500,
          'unit': 'GRAM',
          'storage_mode': 'REFRIGERATED',
          'status': 'ACTIVE',
          'source': 'MANUAL',
          'created_at': '2026-08-30T00:00:00.000Z',
        },
      );
      when(
        () => api.post(
          ApiPaths.freshnessAssessment('batch-1'),
          body: any(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).thenAnswer(
        (_) async => {
          'assessment_id': 'asm-1',
          'batch_id': 'batch-1',
          'blocked': false,
          'expires_at': '2030-01-04T00:00:00Z',
        },
      );

      final router = GoRouter(
        routes: [
          GoRoute(
            path: '/',
            builder: (_, _) => const Scaffold(body: Text('pantry')),
          ),
          GoRoute(
            path: '/add',
            builder: (_, _) => const AddIngredientScreen(),
          ),
        ],
      );
      await tester.pumpWidget(
        ProviderScope(
          overrides: [apiClientProvider.overrideWithValue(api)],
          child: MaterialApp.router(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            routerConfig: router,
          ),
        ),
      );
      unawaited(router.push('/add'));
      await tester.pumpAndSettle();

      // Type a free-text name, then leave the field → smart parser runs.
      await tester.enterText(find.byType(TextField).first, 'thịt ba rọi');
      FocusManager.instance.primaryFocus?.unfocus();
      await tester.pumpAndSettle();

      expect(find.text('Thịt ba chỉ'), findsOneWidget); // normalized name
      expect(find.text('500'), findsOneWidget); // quantity from the text
      expect(find.text('Nhập hạn'), findsOneWidget);
      expect(find.text('Kiểm tra hạn nhanh'), findsOneWidget);

      // FreshCheck: answer, preview, accept.
      await tester.tap(find.text('Kiểm tra hạn nhanh'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Xem hạn ước tính'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Dùng hạn này (04/01/2030)'));
      await tester.pumpAndSettle();

      expect(find.textContaining('FreshCheck: còn 2–3 ngày'), findsOneWidget);

      // Save.
      await tester.tap(find.text('Thêm vào kho'));
      await tester.pumpAndSettle();

      final created =
          verify(
                () => api.post(
                  ApiPaths.inventoryBatches,
                  body: captureAny(named: 'body'),
                  headers: any(named: 'headers'),
                ),
              ).captured.single
              as Map<String, dynamic>;
      expect(created['master_ingredient_id'], 'ing-7');
      expect(created.containsKey('custom_name'), isFalse);
      // The FreshCheck estimate is never sent as a printed expiry date.
      expect(created.containsKey('expires_at'), isFalse);

      final assessed =
          verify(
                () => api.post(
                  ApiPaths.freshnessAssessment('batch-1'),
                  body: captureAny(named: 'body'),
                  headers: any(named: 'headers'),
                ),
              ).captured.single
              as Map<String, dynamic>;
      expect(assessed['answers'], {'smell': 'fresh'});
    },
  );
}
