import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/features/pantry/data/datasources/freshness_remote_data_source.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient mockApi;
  late FreshnessRemoteDataSource dataSource;

  setUp(() {
    mockApi = _MockApiClient();
    dataSource = FreshnessRemoteDataSource(mockApi);
  });

  group('FreshnessRemoteDataSource', () {
    test('getQuestions returns questions DTO on success', () async {
      when(() => mockApi.get(
            any(),
            query: any(named: 'query'),
          )).thenAnswer((_) async => {
            'kb_version': '0.3.0',
            'freshcheck_ingredient_id': 'fc_tomato',
            'archetype_id': 'solanaceae',
            'questions': [
              {
                'axis': 'smell',
                'question_vi': 'Mùi cà chua ra sao?',
                'options': [
                  {'value': 'fresh', 'label_vi': 'Thơm tự nhiên'},
                  {'value': 'sour', 'label_vi': 'Chua'},
                ],
                'default': 'fresh',
              }
            ],
          });

      final res = await dataSource.getQuestions('ing-1');
      expect(res.kbVersion, '0.3.0');
      expect(res.questions.length, 1);
      expect(res.questions.first.axis, 'smell');
    });

    test('assessBatch returns assessment result DTO on success', () async {
      when(() => mockApi.post(
            any(),
            body: any(named: 'body'),
            query: any(named: 'query'),
            headers: any(named: 'headers'),
          )).thenAnswer((_) async => {
            'assessment_id': 'asm-123',
            'batch_id': 'b1',
            'blocked': false,
            'tier': 'FRESH',
            'score': 0.95,
            'remaining_days_min': 3,
            'remaining_days_max': 5,
            'reasons_vi': ['Còn tươi'],
            'storage_tips_vi': ['Bảo quản ngăn mát'],
            'expires_at': '2026-10-25T00:00:00Z',
          });

      final result = await dataSource.assessBatch(
        'b1',
        answers: {'smell': 'fresh'},
      );

      expect(result.batchId, 'b1');
      expect(result.tier, 'FRESH');
      expect(result.blocked, isFalse);
      expect(result.remainingDaysMin, 3);
      expect(result.remainingDaysMax, 5);
      expect(result.reasonsVi.first, 'Còn tươi');
    });
  });
}
