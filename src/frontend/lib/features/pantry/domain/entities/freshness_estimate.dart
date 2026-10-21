import 'package:freezed_annotation/freezed_annotation.dart';

part 'freshness_estimate.freezed.dart';

/// A FreshCheck preview the user accepted before saving a new item.
///
/// [expiresAt] is only displayed — it is never sent as `expires_at` on batch
/// creation (the backend would record it as a printed manufacturer date). After
/// the batch is saved, [answers] and [otherAnswers] (free-text "Khác") are
/// submitted to the batch assessment so the backend records the expiry as an
/// estimate with an audit trail.
@freezed
abstract class FreshnessEstimate with _$FreshnessEstimate {
  const factory FreshnessEstimate({
    required Map<String, String> answers,
    @Default(<String, String>{}) Map<String, String> otherAnswers,
    required DateTime expiresAt,
    int? remainingDaysMin,
    int? remainingDaysMax,
    @Default(false) bool blocked,
  }) = _FreshnessEstimate;
}
