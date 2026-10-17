import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/features/settings/data/datasources/rating_remote_data_source.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient mockApi;
  late RatingRemoteDataSource dataSource;

  setUp(() {
    mockApi = _MockApiClient();
    dataSource = RatingRemoteDataSource(mockApi);
  });

  group('RatingRemoteDataSource', () {
    test('submitRating calls post successfully', () async {
      when(() => mockApi.post(
            any(),
            query: any(named: 'query'),
            body: any(named: 'body'),
            headers: any(named: 'headers'),
          )).thenAnswer((_) async => {'success': true});

      await expectLater(
        dataSource.submitRating(
          rating: 5,
          feedback: 'Ứng dụng tuyệt vời!',
        ),
        completes,
      );
    });

    test('submitRating handles null feedback', () async {
      when(() => mockApi.post(
            any(),
            query: any(named: 'query'),
            body: any(named: 'body'),
            headers: any(named: 'headers'),
          )).thenAnswer((_) async => {'success': true});

      await expectLater(
        dataSource.submitRating(rating: 4),
        completes,
      );
    });
  });
}
