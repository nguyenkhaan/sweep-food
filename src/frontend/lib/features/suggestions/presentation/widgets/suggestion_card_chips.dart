import 'package:frontend/core/widgets/suggestion_card.dart';
import 'package:frontend/features/suggestions/domain/entities/dish_suggestion.dart';

/// Maps a [DishSuggestion] to the chip list of a [SuggestionCard].
///
/// Shared by S-01 (`suggestion_list_screen`) and the H-01 Home preview
/// (`home_screen`) so the two never show different chips for the same dish.
extension SuggestionCardChips on DishSuggestion {
  List<SuggestionChip> get cardChips => [
        if (nearExpiryCount > 0)
          (
            label: 'Dùng $nearExpiryCount đồ cận hạn',
            tone: SuggestionChipTone.nearExpiry,
          ),
        (
          label: 'Có sẵn $availabilityPercent%',
          tone: SuggestionChipTone.available,
        ),
        if (toBuyCount > 0)
          (label: 'Cần mua $toBuyCount', tone: SuggestionChipTone.toBuy)
        else
          (label: 'Không cần mua', tone: SuggestionChipTone.available),
      ];
}
