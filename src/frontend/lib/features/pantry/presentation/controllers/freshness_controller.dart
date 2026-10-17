import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/features/pantry/data/datasources/freshness_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/models/freshness_dto.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';

final freshnessRemoteDataSourceProvider =
    Provider<FreshnessRemoteDataSource>((ref) {
  return FreshnessRemoteDataSource(ref.watch(apiClientProvider));
});

final freshnessQuestionsProvider = FutureProvider.autoDispose
    .family<FreshnessQuestionsResponseDto, String>((ref, ingredientId) async {
  final remote = ref.watch(freshnessRemoteDataSourceProvider);
  return remote.getQuestions(ingredientId);
});

class FreshnessAssessmentState {
  const FreshnessAssessmentState({
    this.isLoading = false,
    this.result,
    this.errorMessage,
  });

  final bool isLoading;
  final FreshnessAssessmentResponseDto? result;
  final String? errorMessage;
}

class FreshnessController extends ValueNotifier<FreshnessAssessmentState> {
  FreshnessController(this._ref) : super(const FreshnessAssessmentState());

  final Ref _ref;

  Future<FreshnessAssessmentResponseDto?> submit({
    required String batchId,
    required Map<String, String> answers,
    String? storageMode,
  }) async {
    value = const FreshnessAssessmentState(isLoading: true);

    try {
      final remote = _ref.read(freshnessRemoteDataSourceProvider);
      final res = await remote.assessBatch(
        batchId,
        answers: answers,
        storageMode: storageMode,
      );
      value = FreshnessAssessmentState(result: res);

      // Invalidate pantry list so updated expiry is reflected immediately
      _ref.invalidate(pantryListControllerProvider);
      return res;
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

final freshnessControllerProvider =
    Provider.autoDispose<FreshnessController>((ref) {
  final controller = FreshnessController(ref);
  ref.onDispose(controller.dispose);
  return controller;
});
