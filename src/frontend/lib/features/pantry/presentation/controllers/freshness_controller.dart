import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/features/pantry/data/datasources/freshness_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/models/freshness_dto.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';

final freshnessRemoteDataSourceProvider = Provider<FreshnessRemoteDataSource>((
  ref,
) {
  return FreshnessRemoteDataSource(ref.watch(apiClientProvider));
});

// Keep one result (including an unsupported/error result) per ingredient for
// the app session. Review lists are lazy: auto-disposing rows would otherwise
// request the same FreshCheck mapping again whenever they re-enter the viewport.
final freshnessQuestionsProvider =
    FutureProvider.family<FreshnessQuestionsResponseDto, String>((
      ref,
      ingredientId,
    ) async {
      final remote = ref.watch(freshnessRemoteDataSourceProvider);
      return remote.getQuestions(ingredientId);
    }, retry: (_, _) => null);

class FreshnessAssessmentState {
  const FreshnessAssessmentState({
    this.isLoading = false,
    this.result,
    this.errorMessage,
    this.axisErrors = const {},
  });

  final bool isLoading;
  final FreshnessAssessmentResponseDto? result;
  final String? errorMessage;

  /// Per-axis feedback for free-text answers the backend could not use; shown
  /// under each axis' input box instead of as a general error.
  final Map<String, String> axisErrors;
}

class FreshnessController extends ValueNotifier<FreshnessAssessmentState> {
  FreshnessController(this._ref) : super(const FreshnessAssessmentState());

  final Ref _ref;

  Future<FreshnessAssessmentResponseDto?> submit({
    required String batchId,
    required Map<String, String> answers,
    Map<String, String> otherAnswers = const {},
    String? storageMode,
    DateTime? purchasedAt,
  }) async {
    value = const FreshnessAssessmentState(isLoading: true);

    try {
      final remote = _ref.read(freshnessRemoteDataSourceProvider);
      final res = await remote.assessBatch(
        batchId,
        answers: answers,
        otherAnswers: otherAnswers,
        storageMode: storageMode,
        purchasedAt: purchasedAt,
      );
      value = FreshnessAssessmentState(result: res);

      // Invalidate pantry list so updated expiry is reflected immediately
      _ref.invalidate(pantryListControllerProvider);
      return res;
    } on FreshnessClarificationException catch (e) {
      value = FreshnessAssessmentState(axisErrors: e.axisErrors);
      return null;
    } catch (e) {
      final message = e.toString().contains('MAPPING_UNAVAILABLE')
          ? 'Nguyên liệu này chưa được ánh xạ trong cơ sở dữ liệu cảm quan FreshCheck.'
          : 'Không thể đánh giá độ tươi lúc này. Vui lòng thử lại sau.';
      value = FreshnessAssessmentState(errorMessage: message);
      return null;
    }
  }

  void reset() {
    value = const FreshnessAssessmentState();
  }
}

final freshnessControllerProvider = Provider.autoDispose<FreshnessController>((
  ref,
) {
  final controller = FreshnessController(ref);
  ref.onDispose(controller.dispose);
  return controller;
});
