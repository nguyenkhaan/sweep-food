// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppL10nEn extends AppL10n {
  AppL10nEn([String locale = 'en']) : super(locale);

  @override
  String get appName => 'SweepFood';

  @override
  String get navHome => 'Home';

  @override
  String get navPantry => 'Pantry';

  @override
  String get navSuggestions => 'Suggestions';

  @override
  String get navShopping => 'Shopping';

  @override
  String get navProfile => 'Profile';

  @override
  String get commonRetry => 'Retry';

  @override
  String get commonUndo => 'Undo';

  @override
  String get commonRecommended => 'Suggested';

  @override
  String get commonAllow => 'Allow';

  @override
  String get commonNotNow => 'Not now';

  @override
  String get commonCancel => 'Cancel';

  @override
  String get commonSave => 'Save';

  @override
  String get commonDone => 'Done';

  @override
  String get commonClose => 'Close';

  @override
  String get commonDelete => 'Delete';

  @override
  String get commonEdit => 'Edit';

  @override
  String get commonContinue => 'Continue';

  @override
  String get commonSkip => 'Skip';

  @override
  String get commonComingSoon => 'Coming soon';

  @override
  String get tierEatSoon => 'Eat soon / cook today';

  @override
  String get tierEatSoonShort => 'Eat soon';

  @override
  String get tierFridge => 'Fridge';

  @override
  String get tierFreezer => 'Freezer';

  @override
  String get tierPantryShelf => 'Pantry shelf';

  @override
  String get pantrySortPriority => 'Near expiry';

  @override
  String get pantrySortName => 'Name A–Z';

  @override
  String get pantrySortRecent => 'Recently added';

  @override
  String get pantrySourceLabelScan => 'Label scan';

  @override
  String get pantrySourceReceiptScan => 'Receipt scan';

  @override
  String get pantrySourceVoice => 'Voice entry';

  @override
  String get pantrySourceManual => 'Manual entry';

  @override
  String get pantrySourceCooked => 'Cooked food';

  @override
  String get cookModeExact => 'Use exact amounts';

  @override
  String get cookModeExactDesc => 'Deduct stock per the recipe';

  @override
  String get cookModeHalf => 'Use half';

  @override
  String get cookModeHalfDesc => 'Deduct 50% of the planned amount';

  @override
  String get cookModeAll => 'Use everything on hand';

  @override
  String get cookModeAllDesc => 'Bring these ingredients to 0';

  @override
  String get cookModeCustom => 'Adjust manually';

  @override
  String get cookModeCustomDesc => 'Tune each ingredient';

  @override
  String get mealSlotBreakfast => 'Breakfast';

  @override
  String get mealSlotLunch => 'Lunch';

  @override
  String get mealSlotDinner => 'Dinner';

  @override
  String get mealTypeBreakfast => 'Breakfast';

  @override
  String get mealTypeLunch => 'Lunch';

  @override
  String get mealTypeDinner => 'Dinner';

  @override
  String get reportPeriodWeek => 'This week';

  @override
  String get reportPeriodMonth => 'This month';

  @override
  String get dietBalanced => 'Balanced';

  @override
  String get dietBalancedDesc => 'All food groups, nothing skewed';

  @override
  String get dietHighProtein => 'High protein';

  @override
  String get dietHighProteinDesc => 'Favour meat, fish, eggs, beans';

  @override
  String get dietLowCalorie => 'Low calorie';

  @override
  String get dietLowCalorieDesc => 'Favour dishes under 400 kcal / serving';

  @override
  String get dietMoreVeg => 'More vegetables';

  @override
  String get dietMoreVegDesc => 'Favour dishes rich in vegetables and fibre';

  @override
  String get macroEnergy => 'Energy';

  @override
  String get macroProtein => 'Protein';

  @override
  String get macroCarb => 'Carbs';

  @override
  String get macroFat => 'Fat';

  @override
  String macroKcal(int kcal) {
    return '$kcal kcal';
  }

  @override
  String macroGrams(int grams) {
    return '${grams}g';
  }

  @override
  String get scoreBadgeLabel => 'SCORE';

  @override
  String get confidenceNeedsReview => 'Check this';

  @override
  String get wastePillPeriodThisMonth => 'this month';

  @override
  String wastePillCount(int count) {
    return '$count ingredients';
  }

  @override
  String wastePillUsedBeforeExpiry(String period) {
    return '\nused before expiry $period';
  }

  @override
  String wastePillUsedBeforeExpiryWithKg(String period, String kg) {
    return '\nused before expiry $period · ≈ $kg kg waste avoided';
  }

  @override
  String get expiryNone => 'No expiry';

  @override
  String expiryOverdueDays(int days) {
    return '$days days overdue';
  }

  @override
  String get expiryToday => 'Today';

  @override
  String expiryInDays(int days) {
    return '$days days left';
  }

  @override
  String expiryInMonths(int months) {
    return '$months months left';
  }

  @override
  String expiryInYears(int years) {
    return '$years years left';
  }

  @override
  String get failNetwork => 'No network connection. Check it and try again.';

  @override
  String get failTimeout =>
      'The server took too long to respond. Please try again.';

  @override
  String get failUnauthorized =>
      'Your session has expired. Please sign in again.';

  @override
  String get failForbidden => 'You don\'t have permission for this action.';

  @override
  String get failQuota =>
      'You\'ve used up this feature\'s quota for the month.';

  @override
  String get failParse => 'The response was not in the expected format.';

  @override
  String get failUnknown => 'Something unexpected went wrong.';

  @override
  String get permCameraTitle => 'Allow camera access';

  @override
  String get permMicTitle => 'Allow microphone access';

  @override
  String get permCameraDesc =>
      'SweepFood needs the camera to scan labels and receipts. Photos are only used to extract ingredient info, and are not kept unless you confirm.';

  @override
  String get permMicDesc =>
      'SweepFood needs the microphone to recognise your voice when you read out an ingredient list. Audio is only processed to extract the info.';

  @override
  String get permCameraSettingsHint =>
      'Enable the Camera permission in Settings to scan.';

  @override
  String get permMicSettingsHint =>
      'Enable the Microphone permission in Settings to speak.';

  @override
  String get permCameraRetryHint =>
      'Camera permission not granted — try again and choose \"Allow\".';

  @override
  String get permMicRetryHint =>
      'Microphone permission not granted — try again and choose \"Allow\".';

  @override
  String get permOpenSettings => 'Open Settings';

  @override
  String get permFinePrint => 'You can change this in Settings at any time.';

  @override
  String get commonConfirm => 'Confirm';

  @override
  String get commonBuyShort => '+ Buy';

  @override
  String get cookUpdateFailed => 'Couldn\'t update the pantry. Try again.';

  @override
  String cookConfirmTitle(String name) {
    return 'Did you cook “$name”?';
  }

  @override
  String get cookConfirmSubtitle =>
      'Pick how much you used so the pantry updates';

  @override
  String cookExactWithServings(int servings) {
    return 'Deduct per the recipe ($servings servings)';
  }

  @override
  String get customUsageTitle => 'Adjust amounts used';

  @override
  String get leftoverTitle => 'Leftovers?';

  @override
  String get leftoverSubtitle =>
      'Save what\'s left to the pantry (Eat soon tier) and set a use-soon reminder.';

  @override
  String get leftoverServingsLabel => 'Servings left';

  @override
  String servingsCount(int count) {
    return '$count servings';
  }

  @override
  String get leftoverReminderLabel => 'Remind me';

  @override
  String leftoverReminderInDays(int days) {
    return 'In $days days';
  }

  @override
  String get leftoverSafetyNote =>
      'Cooked food is best within 1–2 days. Check the smell and look before eating.';

  @override
  String get leftoverSaveCta => 'Save leftovers';

  @override
  String get leftoverSaved => 'Leftovers saved to the pantry';

  @override
  String get leftoverSaveFailed => 'Couldn\'t save. Try again.';

  @override
  String get cookResultTitle => 'Pantry updated';

  @override
  String cookResultSaveLeftovers(int count) {
    return 'Save $count leftover servings';
  }

  @override
  String get cookResultViewPantry => 'View pantry';

  @override
  String cookResultWasteKgSuffix(String kg) {
    return ' · ~$kg kg of food kept from waste';
  }

  @override
  String get cookResultUsedNearExpiryPrefix => 'You just used ';

  @override
  String cookResultUsedNearExpiryCount(int count) {
    return '$count near-expiry ingredients';
  }

  @override
  String get cookResultChangesHeader => 'PANTRY CHANGES';

  @override
  String cookResultLowStock(String names) {
    return '$names running low';
  }

  @override
  String get commonNotChosen => 'Not set';

  @override
  String daysCount(int days) {
    return '$days days';
  }

  @override
  String daysApprox(int days) {
    return '~$days days';
  }

  @override
  String get tierAll => 'All';

  @override
  String get pantryTitle => 'Pantry';

  @override
  String pantrySortPrefix(String label) {
    return 'Sort: $label';
  }

  @override
  String get pantryAddIngredient => 'Add ingredient';

  @override
  String get pantrySearchHint => 'Search the pantry…';

  @override
  String get pantryNoResults => 'No results';

  @override
  String get pantryNoResultsBody => 'Try a different filter or keyword.';

  @override
  String get pantryEmptyTitle => 'Your pantry is empty';

  @override
  String get pantryEmptyBody =>
      'Add your first ingredient to get dish suggestions.';

  @override
  String get pantrySectionNear => 'Use soon';

  @override
  String get pantrySectionAll => 'All';

  @override
  String get pantrySectionRest => 'In date';

  @override
  String pantryConsumedAll(String name) {
    return 'Used up $name';
  }

  @override
  String get pantryUpdateFailed => 'Couldn\'t update. Try again.';

  @override
  String get pantryDeleteTitle => 'Delete ingredient?';

  @override
  String pantryDeleteBody(String name) {
    return '“$name” will be removed from the pantry.';
  }

  @override
  String pantryDeleted(String name) {
    return 'Deleted $name';
  }

  @override
  String get pantryDeleteFailed => 'Couldn\'t delete. Try again.';

  @override
  String get pantryNotFoundTitle => 'Ingredient not found';

  @override
  String get pantryNotFoundBody =>
      'It may have been used up or removed from the pantry.';

  @override
  String get pantryDeleteMenu => 'Remove from pantry';

  @override
  String get pantryStatQuantity => 'Quantity';

  @override
  String get pantryStatExpiry => 'Expiry';

  @override
  String get pantryStatPrice => 'Price';

  @override
  String get pantryStatStorage => 'Storage';

  @override
  String get pantryFindDishes => 'Find dishes to cook with this';

  @override
  String get pantryDetailLocation => 'Storage location';

  @override
  String get pantryDetailAdded => 'Added on';

  @override
  String get pantryDetailPacked => 'Packed / bought on';

  @override
  String get pantryDetailSource => 'Entry source';

  @override
  String get pantryDetailShelfRef => 'Reference shelf life';

  @override
  String get pantryDetailCardTitle => 'Details';

  @override
  String get pantryAdjust => 'Adjust';

  @override
  String get pantryConsumeAll => 'Used it all';

  @override
  String pantryItemUpdated(String name) {
    return 'Updated $name';
  }

  @override
  String pantryItemAdded(String name) {
    return 'Added $name to the pantry';
  }

  @override
  String get pantrySaveFailed => 'Couldn\'t save. Check the details.';

  @override
  String get pantryEditTitle => 'Edit ingredient';

  @override
  String get pantryAddTitle => 'Add ingredient';

  @override
  String get pantryFieldName => 'Ingredient name';

  @override
  String get pantryFieldNameHint => 'e.g. Cherry tomatoes';

  @override
  String get pantryFieldCategory => 'Food group';

  @override
  String get pantryFieldCategoryHint => 'e.g. Vegetables';

  @override
  String get pantryFieldStorage => 'Where it\'s stored';

  @override
  String get pantryFieldExpiry => 'Use-by date';

  @override
  String get pantryFieldPrice => 'Price (optional)';

  @override
  String get pantrySaveChanges => 'Save changes';

  @override
  String get pantryAddToPantry => 'Add to pantry';

  @override
  String adjustQtyTitle(String name) {
    return 'Update quantity — $name';
  }

  @override
  String adjustQtySubtitle(String qty, String tier) {
    return 'On hand: $qty · $tier';
  }

  @override
  String get adjustQtyPartial => 'Use some';

  @override
  String get adjustQtyAll => 'Use all';

  @override
  String get adjustQtyRemaining => 'Left after use';

  @override
  String get onbDietTitle => 'How do you want to eat?';

  @override
  String get onbDietSubtitle =>
      'Used to rank dish suggestions. You can change it any time in Settings.';

  @override
  String get onbLater => 'Later';

  @override
  String get onbMethodScan => 'Scan';

  @override
  String get onbMethodVoice => 'Speak';

  @override
  String get onbMethodManual => 'Type';

  @override
  String get onbPantryTitle => 'Add ingredients in seconds';

  @override
  String get onbPantryBody =>
      'Scan a label or receipt to prefill the name, weight and expiry. Hands full? Read it out. No packaging? Type it in fast.';

  @override
  String get onbPantryCta => 'Add your first ingredient';

  @override
  String get suggestionsTitle => 'Suggestions for you';

  @override
  String get suggestionsQuickCook => '≤ 30 min';

  @override
  String get suggestionsEmptyTitle => 'Not enough ingredients to suggest';

  @override
  String get suggestionsEmptyBody =>
      'Add a few ingredients to your pantry to get 3–5 dish suggestions.';

  @override
  String suggestionsCaption(int count) {
    return '$count best dishes for your current pantry · near-expiry first';
  }

  @override
  String get suggestionsWhyScore => 'Why this score?';

  @override
  String chipUseNearExpiry(int count) {
    return 'Uses $count near-expiry';
  }

  @override
  String chipAvailable(int percent) {
    return '$percent% on hand';
  }

  @override
  String chipToBuy(int count) {
    return 'Buy $count';
  }

  @override
  String get chipNoBuy => 'Nothing to buy';

  @override
  String scoreSheetTitle(String name, int score) {
    return 'Why does “$name” score $score?';
  }

  @override
  String get scoreFormula => 'Score = 0.4·E + 0.3·A + 0.2·P + 0.1·U';

  @override
  String get scoreCompE => 'Uses near-expiry stock';

  @override
  String get scoreCompA => 'Share of ingredients on hand';

  @override
  String get scoreCompP => 'Fits servings & preferences';

  @override
  String get scoreCompU => 'Little extra shopping';

  @override
  String get scoreReasonENone => 'Uses no near-expiry ingredients';

  @override
  String scoreReasonE(int count, String list) {
    return 'Uses $count near-expiry ingredients: $list';
  }

  @override
  String scoreReasonA(int percent) {
    return '$percent% of ingredients already in the pantry';
  }

  @override
  String scoreReasonP(int servings, int kcal, int minutes) {
    return '$servings servings · $kcal kcal · $minutes min';
  }

  @override
  String get scoreReasonUNone => 'No extra ingredients to buy';

  @override
  String scoreReasonU(int count) {
    return 'Only $count more ingredients to buy';
  }

  @override
  String get dishDetailTitle => 'Dish details';

  @override
  String dishIngredientsWithServings(int servings) {
    return 'Ingredients · $servings servings';
  }

  @override
  String get dishSeasonings => 'Seasonings';

  @override
  String get dishHowTo => 'Method';

  @override
  String get dishServingsLabel => 'Servings';

  @override
  String get dishCookedThis => 'I cooked this';

  @override
  String dishAddedToShopping(int count) {
    return 'Added $count ingredients to the shopping list';
  }

  @override
  String get dishShoppingNotReady =>
      'Shopping list isn\'t ready — try again later.';

  @override
  String dishAddMissing(int count) {
    return 'Add $count missing ingredients to the shopping list';
  }

  @override
  String get checklistNearExpiry => 'near expiry';

  @override
  String get checklistToBuy => 'to buy';

  @override
  String get macroEstimateNote =>
      'Estimated per serving · source: National Institute of Nutrition';

  @override
  String ingredientCount(int count) {
    return '$count ingredients';
  }

  @override
  String get seeAll => 'See all';

  @override
  String get greetingMorning => 'Good morning';

  @override
  String get greetingNoon => 'Good afternoon';

  @override
  String get greetingAfternoon => 'Good afternoon';

  @override
  String get greetingEvening => 'Good evening';

  @override
  String get homeWhatToEat => 'What\'s for dinner?';

  @override
  String get homeEmptyTitle => 'Your pantry is empty';

  @override
  String get homeEmptyBody =>
      'Add a few ingredients to get dish suggestions and expiry reminders.';

  @override
  String get homeAddFirst => 'Add your first ingredient';

  @override
  String get homeTileSuggestDish => 'Dish ideas';

  @override
  String homeSuggestionCount(int count) {
    return '$count matching dishes';
  }

  @override
  String get homeSuggestFallback => 'Dishes for your pantry';

  @override
  String get homeQuickAdd => 'Quick add';

  @override
  String get homeQuickAddSub => 'Label · Receipt · Voice';

  @override
  String get homeUseSoon => 'Use soon';

  @override
  String get homeNoNearExpiry =>
      'Nothing near expiry. Your pantry is looking fresh!';

  @override
  String get homeSuggestionsLoadFail =>
      'Couldn\'t load suggestions. Pull down to refresh.';

  @override
  String get wdMon => 'Mon';

  @override
  String get wdTue => 'Tue';

  @override
  String get wdWed => 'Wed';

  @override
  String get wdThu => 'Thu';

  @override
  String get wdFri => 'Fri';

  @override
  String get wdSat => 'Sat';

  @override
  String get wdSun => 'Sun';

  @override
  String get mealPlanTitle => 'Weekly plan';

  @override
  String get mealPlanGenerateShopping => 'Create shopping list';

  @override
  String get mealPlanPickDish => 'Pick a dish';

  @override
  String get mealPlanPickDishSub => 'From suggestions that fit your pantry';

  @override
  String get mealSlotChosen => 'Chosen dish';

  @override
  String get mealSlotAdd => '+ Add';

  @override
  String get reportsTitle => 'Waste reduction';

  @override
  String get reportsEmptyTitle => 'No data yet';

  @override
  String get reportsEmptyBody =>
      'Cook a few dishes with near-expiry ingredients to see how much you save.';

  @override
  String get reportsWeeklyCard => 'Ingredients saved by week';

  @override
  String get reportsByCategoryCard => 'By food group';

  @override
  String reportsHeroPeriod(String period) {
    return '$period · ingredients used before expiry';
  }

  @override
  String reportsHeroDetail(String kg, int dishes) {
    return '≈ $kg of food kept from waste · $dishes dishes cooked';
  }

  @override
  String get prefsTitle => 'Preferences';

  @override
  String get prefsGroupMeal => 'Meals';

  @override
  String get prefsDietary => 'Dietary preference';

  @override
  String get prefsUnit => 'Default unit';

  @override
  String get prefsCurrency => 'Display currency';

  @override
  String get prefsCurrencyValue => 'VND (đ)';

  @override
  String get prefsGroupAppearance => 'Appearance';

  @override
  String get prefsLanguage => 'Language';

  @override
  String get langVi => 'Tiếng Việt';

  @override
  String get langEn => 'English';

  @override
  String get prefsTheme => 'Theme';

  @override
  String get themeLight => 'Light';

  @override
  String get themeDark => 'Dark';

  @override
  String get themeSystem => 'System';

  @override
  String get catVegetables => 'Vegetables';

  @override
  String get catMeatSeafood => 'Meat & seafood';

  @override
  String get catSpices => 'Spices';

  @override
  String get catDairyEgg => 'Dairy & eggs';

  @override
  String get catDryGoods => 'Dry goods';

  @override
  String get catOther => 'Other';

  @override
  String scanSaveError(String error) {
    return 'Error saving ingredient: $error';
  }

  @override
  String scanAddedToPantry(String name) {
    return 'Added $name to the pantry!';
  }

  @override
  String scanAddedCountToPantry(int count) {
    return 'Added $count ingredients to the pantry!';
  }

  @override
  String get scanNoName => 'Name unclear';

  @override
  String get scanNeedsCheckShort => 'Check';

  @override
  String get scanAddRow => 'Add row';

  @override
  String get chooserScanLabel => 'Scan label';

  @override
  String get chooserScanLabelSub =>
      'Photograph the weight label on packaged goods';

  @override
  String get chooserScanReceipt => 'Scan receipt';

  @override
  String get chooserScanReceiptSub =>
      'Photograph a receipt, add many items at once';

  @override
  String get chooserVoice => 'Speak';

  @override
  String get chooserVoiceSub => 'Read out ingredient names and amounts';

  @override
  String get chooserManual => 'Type';

  @override
  String get chooserManualSub => 'Pick from the ingredient catalog';

  @override
  String get camModeLabel => 'Label';

  @override
  String get camModeReceipt => 'Receipt';

  @override
  String camScanTitle(String kind) {
    return 'Scan $kind';
  }

  @override
  String get camNoCamera => 'This device has no camera.';

  @override
  String camOpenError(String error) {
    return 'Couldn\'t open the camera: $error';
  }

  @override
  String get camNoFlash => 'The flash isn\'t available on this device.';

  @override
  String camShootError(String error) {
    return 'Couldn\'t take the photo: $error';
  }

  @override
  String camGalleryError(String error) {
    return 'Couldn\'t open the photo library: $error';
  }

  @override
  String get camReading => 'Reading the details…';

  @override
  String get camOpening => 'Opening the camera…';

  @override
  String get camGuideLabel =>
      'Put the weight label in the frame, hold the phone level';

  @override
  String get camGuideReceipt => 'Fit the whole receipt in the frame';

  @override
  String get camPermissionNeeded =>
      'Camera permission is needed to scan directly.';

  @override
  String get camGrantPermission => 'Grant camera permission';

  @override
  String get camUseGallery => 'Use an existing photo';

  @override
  String get reviewLabelTitle => 'Check the details';

  @override
  String reviewFieldsRead(int count) {
    return 'Read $count fields. Check the flagged ones before saving.';
  }

  @override
  String get reviewNetWeight => 'Net weight';

  @override
  String get reviewPackedDate => 'Packed on';

  @override
  String get reviewStorageTier => 'Storage tier';

  @override
  String get reviewCategory => 'Category';

  @override
  String get reviewNameHint => 'Enter the ingredient name';

  @override
  String get reviewUnit => 'Unit';

  @override
  String get reviewPurchasePrice => 'Purchase price (VND)';

  @override
  String get reviewPriceHint => 'e.g. 18000';

  @override
  String get reviewPickCategory => 'Pick a category';

  @override
  String get reviewLabelPhoto => 'Label photo';

  @override
  String get reviewRetake => 'Retake';

  @override
  String reviewReceiptTitle(int count) {
    return 'Receipt — $count items';
  }

  @override
  String reviewSelectedOf(int count) {
    return ' / $count items selected';
  }

  @override
  String get reviewDeselectAll => 'Deselect all';

  @override
  String get reviewSelectAll => 'Select all';

  @override
  String reviewAddCount(int count) {
    return 'Add $count items to the pantry';
  }

  @override
  String get reviewPickAtLeastOne => 'Pick at least 1 item';

  @override
  String get reviewEditItem => 'Edit ingredient';

  @override
  String get reviewRemoveItem => 'Remove this item';

  @override
  String get voiceCaptureTitle => 'Speak to add';

  @override
  String get voiceCapturePrompt => 'Read out ingredient names and amounts';

  @override
  String get voiceCaptureExample =>
      'e.g. “200g beef, 1 bunch of spinach, 3 eggs”';

  @override
  String get voiceListening => 'Listening…';

  @override
  String get voiceMicOff =>
      'Couldn\'t start the mic — go ahead and speak, then check';

  @override
  String get voiceStopReview => 'Stop & review';

  @override
  String get voiceReviewTitle => 'Check the result';

  @override
  String get voiceRerecord => 'Record again';

  @override
  String voiceParsedCount(int count) {
    return 'Parsed $count ingredients';
  }

  @override
  String voiceAddCount(int count) {
    return 'Add $count ingredients';
  }

  @override
  String get scanFailLabelTitle => 'Couldn\'t read the label';

  @override
  String get scanFailReceiptTitle => 'Couldn\'t read the receipt';

  @override
  String get scanFailVoiceTitle => 'Didn\'t catch that';

  @override
  String get scanFailVoiceReason1 => 'Too much background noise';

  @override
  String get scanFailVoiceReason2 => 'Spoken too fast or too quietly';

  @override
  String get scanFailVoiceReason3 => 'The mic was covered';

  @override
  String get scanFailImgReason1 => 'Photo is blurry or at an angle';

  @override
  String get scanFailImgReason2 => 'Label is torn or faded';

  @override
  String get scanFailImgReason3 => 'Not enough light';

  @override
  String get scanFailRerecord => 'Record again';

  @override
  String featureComingInMilestone(String milestone) {
    return 'Coming in $milestone';
  }

  @override
  String get authSignIn => 'Sign in';

  @override
  String get authSignUp => 'Sign up';

  @override
  String get authCreateAccount => 'Create account';

  @override
  String get authEmail => 'Email';

  @override
  String get authPassword => 'Password';

  @override
  String get authFullName => 'Full name';

  @override
  String get authFullNameHint => 'Jane Doe';

  @override
  String get authPasswordHint => 'At least 8 characters';

  @override
  String get authForgotQ => 'Forgot password?';

  @override
  String get authForgotTitle => 'Forgot password';

  @override
  String get authInvalidEmail => 'Invalid email';

  @override
  String get authEnterPassword => 'Enter a password';

  @override
  String get authEnterName => 'Enter your full name';

  @override
  String get authPasswordTooShort => 'At least 8 characters';

  @override
  String get welcomeSlide1Title => 'Turn what you have into meals';

  @override
  String get welcomeSlide1Body =>
      'SweepFood tracks expiry and always surfaces what to use first.';

  @override
  String get welcomeSlide2Title => 'Dishes that fit your pantry';

  @override
  String get welcomeSlide2Body =>
      '3–5 dishes at a time, scored by what\'s on hand and what\'s about to expire.';

  @override
  String get welcomeSlide3Title => 'Use it up, waste less';

  @override
  String get welcomeSlide3Body =>
      'See how many ingredients you used before expiry — in kg of waste avoided.';

  @override
  String get welcomeStart => 'Get started';

  @override
  String get welcomeHaveAccount => 'Already have an account? Sign in';

  @override
  String get loginSubtitle => 'Keep managing your pantry';

  @override
  String get loginNoAccount => 'No account yet? ';

  @override
  String get loginFailed => 'Sign-in failed. Please try again.';

  @override
  String get registerSubtitle => 'Start saving food with SweepFood';

  @override
  String get registerHaveAccount => 'Already have an account? ';

  @override
  String get registerNeedTerms => 'You must agree to the Terms to continue.';

  @override
  String get termsPrefix => 'I agree to the ';

  @override
  String get termsOfUse => 'Terms of Use';

  @override
  String get termsAnd => ' and ';

  @override
  String get termsPrivacy => 'Privacy Policy';

  @override
  String get forgotSubtitle =>
      'Enter your account email and we\'ll send a reset link.';

  @override
  String get forgotSendLink => 'Send link';

  @override
  String get forgotBackToLogin => 'Back to sign in';

  @override
  String forgotSentTo(String email) {
    return 'Sent to $email';
  }

  @override
  String get forgotCheckInbox =>
      'Check your inbox (including spam). The link is valid for 30 minutes.';

  @override
  String get commonYou => 'You';

  @override
  String get dayToday => 'Today';

  @override
  String get dayYesterday => 'Yesterday';

  @override
  String get willOpenInBrowser => 'Opens in your browser.';

  @override
  String get notifTitle => 'Notifications';

  @override
  String get notifMarkAllRead => 'Mark all read';

  @override
  String get notifEmptyTitle => 'No notifications yet';

  @override
  String get notifEmptyBody =>
      'Expiry reminders and waste-reduction recaps will show up here.';

  @override
  String get nearExpiryNotFound => 'This ingredient isn\'t in your pantry.';

  @override
  String get nearExpiryMarkUsed => 'Mark as used';

  @override
  String get nearExpirySeeSuggestions => 'See suggestions';

  @override
  String get expiryTipVeg =>
      'Leafy greens are best used the same day for freshness and nutrition. Check for wilted or slimy leaves before cooking.';

  @override
  String get expiryTipFruit =>
      'Fruit ripens fast at room temperature. Refrigerate to keep it 2–3 days longer; use it as soon as the skin starts to wrinkle.';

  @override
  String get expiryTipMeat =>
      'Fresh meat in the fridge is best cooked within 1–2 days. If you can\'t get to it, freeze right away.';

  @override
  String get expiryTipFish =>
      'Fish and seafood spoil quickly — cook the same day or freeze. Discard if it smells strongly fishy.';

  @override
  String get expiryTipDairy =>
      'Keep milk and dairy refrigerated below 4°C. Use before the date and check the smell before drinking.';

  @override
  String get expiryTipEgg =>
      'Refrigerated eggs keep for a few weeks. Float test: an egg that floats is old.';

  @override
  String get expiryTipDefault =>
      'Use this ingredient soon. Always check colour, smell and texture before cooking.';

  @override
  String get settingsGroupAccount => 'Account';

  @override
  String get settingsProfilePassword => 'Profile & password';

  @override
  String get settingsPlan => 'Plan';

  @override
  String get settingsPremiumSoon => 'Premium coming soon';

  @override
  String get settingsPantrySharing => 'Share pantry';

  @override
  String get settingsGroupMealPlanning => 'Meal planning';

  @override
  String get settingsWasteReport => 'Waste-reduction report';

  @override
  String get settingsGroupApp => 'App';

  @override
  String get settingsGroupOther => 'Other';

  @override
  String get settingsAboutData => 'About & data sources';

  @override
  String get settingsSignOut => 'Sign out';

  @override
  String get signOutConfirmTitle => 'Sign out?';

  @override
  String get signOutConfirmBody =>
      'You\'ll need to sign in again to use SweepFood.';

  @override
  String get planFullFree => 'Full version · free';

  @override
  String get planPremiumDeveloping =>
      'Premium (sync, advanced reports…) in development';

  @override
  String get planInterested => 'Interested';

  @override
  String get aboutTitle => 'About & data';

  @override
  String get aboutVersion => 'Version 1.0.0 (MVP)';

  @override
  String get aboutDataSources => 'Data sources';

  @override
  String get aboutNutritionData => 'Food nutrition values';

  @override
  String get aboutNutritionSource => 'National Institute of Nutrition';

  @override
  String get aboutShelfLifeData => 'Reference shelf life';

  @override
  String get aboutDisclaimer =>
      'Nutrition and shelf-life info are estimates only, and do not replace advice from a nutritionist or medical professional. Always check colour, smell and texture before use.';

  @override
  String get aboutRateApp => 'Rate the app';

  @override
  String get aboutThanks => 'Thank you!';

  @override
  String get notifSettingsTypesHeader => 'NOTIFICATION TYPES';

  @override
  String get notifTypeNearExpiry => 'Near-expiry alerts';

  @override
  String get notifTypeNearExpirySub => 'When an ingredient is about to expire';

  @override
  String get notifTypeDailySuggestions => 'Daily dish suggestions';

  @override
  String get notifTypeWeeklyReport => 'Weekly report';

  @override
  String get notifTypePostCook => 'Post-cook reminder';

  @override
  String get notifTypePromos => 'Promos & tips';

  @override
  String get notifSettingsTiming => 'Timing';

  @override
  String get notifRemindAt => 'Near-expiry reminder at';

  @override
  String get notifDnd => 'Do not disturb';

  @override
  String get notifDndStart => 'Do-not-disturb start';

  @override
  String get notifDndEnd => 'Do-not-disturb end';

  @override
  String get pantrySharingIntro =>
      'Invite up to 4 people to view and update the pantry. Every change syncs to all members.';

  @override
  String get pantrySharingFootnote =>
      'Members can add, edit and delete ingredients and see dish suggestions. Only the pantry owner can remove members.';

  @override
  String get pantrySharingInvite => 'Invite member';

  @override
  String get pantryMemberInvited => 'Invited · awaiting confirmation';

  @override
  String get pantryRoleOwner => 'Pantry owner';

  @override
  String get pantryRoleEditor => 'Can edit';

  @override
  String get profileGroupInfo => 'Info';

  @override
  String get profileEditSoon =>
      'Editing your profile is coming in a later version.';

  @override
  String get profileGroupSecurity => 'Security';

  @override
  String get profileChangePassword => 'Change password';

  @override
  String get profileChangePasswordSoon =>
      'Changing your password is coming in a later version.';

  @override
  String get profileDeleteAccount => 'Delete account';

  @override
  String get profileDeleteConfirmTitle => 'Delete account?';

  @override
  String get profileDeleteConfirmBody =>
      'All pantry data will be permanently deleted. This cannot be undone.';

  @override
  String get profileDeleteRequested =>
      'Your account deletion request has been recorded.';

  @override
  String minutesLabel(int minutes) {
    return '$minutes min';
  }

  @override
  String dishMetaPrep(int minutes) {
    return '$minutes min prep';
  }

  @override
  String dishMetaKcalPerServing(int kcal) {
    return '$kcal kcal / serving';
  }

  @override
  String get shoppingTitle => 'Shopping list';

  @override
  String get shoppingAddItem => 'Add item';

  @override
  String get shoppingEmptyTitle => 'No shopping list yet';

  @override
  String get shoppingEmptyBody =>
      'Plan your week, then build a shopping list in one tap.';

  @override
  String get shoppingPlanWeek => 'Plan the week';

  @override
  String get shoppingShowInStock => 'Show ingredients already in the pantry';

  @override
  String get shoppingEstimate => 'Estimate';

  @override
  String shoppingToBuyCount(int count) {
    return '$count ingredients to buy';
  }

  @override
  String get shoppingItemName => 'Item name';

  @override
  String get shoppingCategoryOptional => 'Category (optional)';

  @override
  String get shoppingCategoryHint => 'Vegetables, Meat & seafood, …';

  @override
  String get shoppingAddToList => 'Add to list';

  @override
  String get shoppingHavePill => 'have';

  @override
  String get shoppingFromRecipe => 'From recipe';

  @override
  String get subCurrentPlan => 'You\'re on';

  @override
  String get subInterestRegistered => 'Premium interest registered';

  @override
  String get subInterestCta => 'Interested in Premium — notify me at launch';

  @override
  String get subDisclaimer =>
      'During the trial, all features are free. Later, some advanced features (multi-device sync, pantry sharing, detailed reports) will move to Premium — you\'ll get notice first.';

  @override
  String get subTierFree => 'Full version · free';

  @override
  String get subTierMonthly => 'Premium monthly';

  @override
  String get subTierYearly => 'Premium yearly';

  @override
  String get subTierFamily => 'Premium family';

  @override
  String get paywallTitle => 'SweepFood Premium is coming';

  @override
  String get paywallSubtitle =>
      'You\'re using every feature for free right now. Sign up to be notified at launch and get early perks.';

  @override
  String get paywallBenefit1 => 'Unlimited pantry';

  @override
  String get paywallBenefit2 => 'Unlimited label & receipt scans';

  @override
  String get paywallBenefit3 => 'Weekly plan & shopping list';

  @override
  String get paywallBenefit4 => 'Daily nutrition goals';

  @override
  String get paywallBenefit5 => 'Food-saved reports';

  @override
  String get paywallBenefit6 => 'Pantry sharing for up to 4 people';

  @override
  String get paywallSubmitted => 'Got it — thank you!';

  @override
  String get paywallNotifyMe => 'Notify me at launch';

  @override
  String get paywallFinePrint =>
      'No charge yet · pricing & plans are still being validated';
}
