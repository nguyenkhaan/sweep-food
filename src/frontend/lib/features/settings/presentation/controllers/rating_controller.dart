import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/features/settings/data/datasources/rating_remote_data_source.dart';

final ratingRemoteDataSourceProvider = Provider<RatingRemoteDataSource>((ref) {
  return RatingRemoteDataSource(ref.watch(apiClientProvider));
});

class RatingSubmitState {
  const RatingSubmitState({
    this.isLoading = false,
    this.isSuccess = false,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSuccess;
  final String? errorMessage;
}

class RatingController extends ValueNotifier<RatingSubmitState> {
  RatingController(this._ref) : super(const RatingSubmitState());

  final Ref _ref;

  Future<bool> submitRating({
    required double rating,
    String? feedback,
  }) async {
    value = const RatingSubmitState(isLoading: true);
    try {
      final remote = _ref.read(ratingRemoteDataSourceProvider);
      await remote.submitRating(rating: rating, feedback: feedback);
      value = const RatingSubmitState(isSuccess: true);
      return true;
    } catch (_) {
      value = const RatingSubmitState(
        errorMessage: 'Gửi đánh giá không thành công. Vui lòng thử lại sau.',
      );
      return false;
    }
  }

  void reset() {
    value = const RatingSubmitState();
  }
}

final ratingControllerProvider =
    Provider.autoDispose<RatingController>((ref) {
  final controller = RatingController(ref);
  ref.onDispose(controller.dispose);
  return controller;
});
