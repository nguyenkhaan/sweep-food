import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

/// Which meal the user is cooking (S-01 filter).
enum MealType {
  breakfast('breakfast'),
  lunch('lunch'),
  dinner('dinner');

  const MealType(this.wire);
  final String wire;

  String label(AppL10n l10n) => switch (this) {
    MealType.breakfast => l10n.mealTypeBreakfast,
    MealType.lunch => l10n.mealTypeLunch,
    MealType.dinner => l10n.mealTypeDinner,
  };
}

/// Body for `POST /recommendations`. The real backend accepts `{request: string}`
/// (1..1000 chars, non-blank) representing the user query prompt.
class SuggestionRequest {
  const SuggestionRequest({
    this.request,
    this.prompt,
    this.dietaryPreference,
    this.maxCookTimeMin,
    this.mealType,
    this.limit = AppConstants.maxSuggestions,
  });

  /// Explicit free-text request for `POST /recommendations`.
  final String? request;

  /// Free-text search/filter prompt typed by the user.
  final String? prompt;

  final DietaryPreference? dietaryPreference;
  final int? maxCookTimeMin;
  final MealType? mealType;
  final int limit;

  SuggestionRequest copyWith({
    String? request,
    String? prompt,
    DietaryPreference? dietaryPreference,
    int? maxCookTimeMin,
    MealType? mealType,
    int? limit,
    bool clearRequest = false,
    bool clearPrompt = false,
    bool clearDietaryPreference = false,
    bool clearMaxCookTime = false,
    bool clearMealType = false,
  }) {
    return SuggestionRequest(
      request: clearRequest ? null : request ?? this.request,
      prompt: clearPrompt ? null : prompt ?? this.prompt,
      dietaryPreference: clearDietaryPreference
          ? null
          : dietaryPreference ?? this.dietaryPreference,
      maxCookTimeMin: clearMaxCookTime
          ? null
          : maxCookTimeMin ?? this.maxCookTimeMin,
      mealType: clearMealType ? null : mealType ?? this.mealType,
      limit: limit ?? this.limit,
    );
  }

  Map<String, dynamic> toBody() {
    final text = _buildRequestText();
    return {'request': text};
  }

  String _buildRequestText() {
    if (request != null && request!.trim().isNotEmpty) {
      final trimmed = request!.trim();
      return trimmed.length > 1000 ? trimmed.substring(0, 1000) : trimmed;
    }
    final parts = <String>[];
    if (prompt != null && prompt!.trim().isNotEmpty) {
      parts.add(prompt!.trim());
    }
    if (mealType != null) {
      parts.add(switch (mealType!) {
        MealType.breakfast => 'Bữa sáng',
        MealType.lunch => 'Bữa trưa',
        MealType.dinner => 'Bữa tối',
      });
    }
    if (maxCookTimeMin != null) {
      parts.add('Nấu nhanh ≤ $maxCookTimeMin phút');
    }
    if (dietaryPreference != null) {
      parts.add(switch (dietaryPreference!) {
        DietaryPreference.balanced => 'Cân bằng',
        DietaryPreference.moreVeg => 'Nhiều rau',
        DietaryPreference.highProtein => 'Giàu đạm',
        DietaryPreference.lowCalorie => 'Ít calo',
      });
    }
    if (parts.isEmpty) {
      return 'Gợi ý món ăn hôm nay';
    }
    final combined = parts.join(', ');
    return combined.length > 1000 ? combined.substring(0, 1000) : combined;
  }
}
