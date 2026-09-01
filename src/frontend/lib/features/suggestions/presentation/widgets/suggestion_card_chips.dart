import 'package:sweepfood/core/widgets/suggestion_card.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

/// Maps a [DishSuggestion] to the chip list of a [SuggestionCard].
///
/// Shared by S-01 (`suggestion_list_screen`) and the H-01 Home preview
/// (`home_screen`) so the two never show different chips for the same dish.
extension SuggestionCardChips on DishSuggestion {
  List<SuggestionChip> cardChips(AppL10n l10n) => [
    if (nearExpiryCount > 0)
      (
        label: l10n.chipUseNearExpiry(nearExpiryCount),
        tone: SuggestionChipTone.nearExpiry,
      ),
    (
      label: l10n.chipAvailable(availabilityPercent),
      tone: SuggestionChipTone.available,
    ),
    if (toBuyCount > 0)
      (label: l10n.chipToBuy(toBuyCount), tone: SuggestionChipTone.toBuy)
    else
      (label: l10n.chipNoBuy, tone: SuggestionChipTone.available),
  ];
}
