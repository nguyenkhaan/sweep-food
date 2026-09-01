// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Vietnamese (`vi`).
class AppL10nVi extends AppL10n {
  AppL10nVi([String locale = 'vi']) : super(locale);

  @override
  String get appName => 'SweepFood';

  @override
  String get navHome => 'Trang chủ';

  @override
  String get navPantry => 'Kho';

  @override
  String get navSuggestions => 'Gợi ý';

  @override
  String get navShopping => 'Mua sắm';

  @override
  String get navProfile => 'Cá nhân';

  @override
  String get commonRetry => 'Thử lại';

  @override
  String get commonUndo => 'Hoàn tác';

  @override
  String get commonRecommended => 'Gợi ý';

  @override
  String get commonAllow => 'Cho phép';

  @override
  String get commonNotNow => 'Không phải bây giờ';

  @override
  String get commonCancel => 'Hủy';

  @override
  String get commonSave => 'Lưu';

  @override
  String get commonDone => 'Xong';

  @override
  String get commonClose => 'Đóng';

  @override
  String get commonDelete => 'Xoá';

  @override
  String get commonEdit => 'Sửa';

  @override
  String get commonContinue => 'Tiếp tục';

  @override
  String get commonSkip => 'Bỏ qua';

  @override
  String get commonComingSoon => 'Sắp có';

  @override
  String get tierEatSoon => 'Ăn liền / Nấu trong ngày';

  @override
  String get tierEatSoonShort => 'Ăn liền';

  @override
  String get tierFridge => 'Ngăn mát';

  @override
  String get tierFreezer => 'Ngăn đông';

  @override
  String get tierPantryShelf => 'Kệ đồ khô';

  @override
  String get pantrySortPriority => 'Cận hạn';

  @override
  String get pantrySortName => 'Tên A–Z';

  @override
  String get pantrySortRecent => 'Mới thêm';

  @override
  String get pantrySourceLabelScan => 'Quét tem nhãn';

  @override
  String get pantrySourceReceiptScan => 'Quét hóa đơn';

  @override
  String get pantrySourceVoice => 'Nhập bằng giọng nói';

  @override
  String get pantrySourceManual => 'Nhập tay';

  @override
  String get pantrySourceCooked => 'Thức ăn đã nấu';

  @override
  String get cookModeExact => 'Dùng đúng định lượng';

  @override
  String get cookModeExactDesc => 'Trừ kho theo công thức';

  @override
  String get cookModeHalf => 'Dùng một nửa';

  @override
  String get cookModeHalfDesc => 'Trừ 50% lượng dự kiến';

  @override
  String get cookModeAll => 'Dùng hết những gì đang có';

  @override
  String get cookModeAllDesc => 'Đưa các nguyên liệu này về 0';

  @override
  String get cookModeCustom => 'Tự điều chỉnh';

  @override
  String get cookModeCustomDesc => 'Chỉnh từng nguyên liệu';

  @override
  String get mealSlotBreakfast => 'Sáng';

  @override
  String get mealSlotLunch => 'Trưa';

  @override
  String get mealSlotDinner => 'Tối';

  @override
  String get mealTypeBreakfast => 'Bữa sáng';

  @override
  String get mealTypeLunch => 'Bữa trưa';

  @override
  String get mealTypeDinner => 'Bữa tối';

  @override
  String get reportPeriodWeek => 'Tuần này';

  @override
  String get reportPeriodMonth => 'Tháng này';

  @override
  String get dietBalanced => 'Cân bằng';

  @override
  String get dietBalancedDesc => 'Đủ nhóm chất, không thiên lệch';

  @override
  String get dietHighProtein => 'Nhiều protein';

  @override
  String get dietHighProteinDesc => 'Ưu tiên thịt, cá, trứng, đậu';

  @override
  String get dietLowCalorie => 'Ít năng lượng';

  @override
  String get dietLowCalorieDesc => 'Ưu tiên món dưới 400 kcal / khẩu phần';

  @override
  String get dietMoreVeg => 'Nhiều rau';

  @override
  String get dietMoreVegDesc => 'Ưu tiên món giàu rau củ, chất xơ';

  @override
  String get macroEnergy => 'Năng lượng';

  @override
  String get macroProtein => 'Đạm';

  @override
  String get macroCarb => 'Tinh bột';

  @override
  String get macroFat => 'Chất béo';

  @override
  String macroKcal(int kcal) {
    return '$kcal kcal';
  }

  @override
  String macroGrams(int grams) {
    return '${grams}g';
  }

  @override
  String get scoreBadgeLabel => 'ĐIỂM';

  @override
  String get confidenceNeedsReview => 'Cần kiểm tra';

  @override
  String get wastePillPeriodThisMonth => 'tháng này';

  @override
  String wastePillCount(int count) {
    return '$count nguyên liệu';
  }

  @override
  String wastePillUsedBeforeExpiry(String period) {
    return '\nđã dùng trước hạn $period';
  }

  @override
  String wastePillUsedBeforeExpiryWithKg(String period, String kg) {
    return '\nđã dùng trước hạn $period · ≈ $kg kg tránh bỏ phí';
  }

  @override
  String get expiryNone => 'Không có hạn';

  @override
  String expiryOverdueDays(int days) {
    return 'Quá hạn $days ngày';
  }

  @override
  String get expiryToday => 'Hôm nay';

  @override
  String expiryInDays(int days) {
    return 'Còn $days ngày';
  }

  @override
  String expiryInMonths(int months) {
    return 'Còn $months tháng';
  }

  @override
  String expiryInYears(int years) {
    return 'Còn $years năm';
  }

  @override
  String get failNetwork => 'Không có kết nối mạng. Kiểm tra lại và thử lại.';

  @override
  String get failTimeout => 'Máy chủ phản hồi quá lâu. Vui lòng thử lại.';

  @override
  String get failUnauthorized =>
      'Phiên đăng nhập đã hết hạn. Đăng nhập lại nhé.';

  @override
  String get failForbidden => 'Bạn không có quyền thực hiện thao tác này.';

  @override
  String get failQuota => 'Bạn đã dùng hết lượt cho tính năng này trong tháng.';

  @override
  String get failParse => 'Dữ liệu trả về không đúng định dạng.';

  @override
  String get failUnknown => 'Đã xảy ra lỗi không mong muốn.';

  @override
  String get permCameraTitle => 'Cho phép dùng máy ảnh';

  @override
  String get permMicTitle => 'Cho phép dùng micro';

  @override
  String get permCameraDesc =>
      'SweepFood cần máy ảnh để quét tem nhãn và hóa đơn. Ảnh chỉ dùng để trích xuất thông tin nguyên liệu, không lưu lại nếu bạn không xác nhận.';

  @override
  String get permMicDesc =>
      'SweepFood cần micro để nhận diện giọng nói khi bạn đọc danh sách nguyên liệu. Âm thanh chỉ được xử lý để bóc tách thông tin.';

  @override
  String get permCameraSettingsHint =>
      'Hãy bật quyền Máy ảnh trong Cài đặt để quét.';

  @override
  String get permMicSettingsHint => 'Hãy bật quyền Micro trong Cài đặt để nói.';

  @override
  String get permCameraRetryHint =>
      'Chưa cấp quyền Máy ảnh — hãy thử lại và chọn \"Cho phép\".';

  @override
  String get permMicRetryHint =>
      'Chưa cấp quyền Micro — hãy thử lại và chọn \"Cho phép\".';

  @override
  String get permOpenSettings => 'Mở Cài đặt';

  @override
  String get permFinePrint => 'Bạn có thể đổi trong Cài đặt bất cứ lúc nào.';

  @override
  String get commonConfirm => 'Xác nhận';

  @override
  String get commonBuyShort => '+ Mua';

  @override
  String get cookUpdateFailed => 'Không cập nhật được kho. Thử lại.';

  @override
  String cookConfirmTitle(String name) {
    return 'Bạn đã nấu “$name”?';
  }

  @override
  String get cookConfirmSubtitle =>
      'Chọn lượng nguyên liệu đã dùng để cập nhật kho';

  @override
  String cookExactWithServings(int servings) {
    return 'Trừ kho theo công thức ($servings phần)';
  }

  @override
  String get customUsageTitle => 'Điều chỉnh lượng đã dùng';

  @override
  String get leftoverTitle => 'Còn dư món ăn?';

  @override
  String get leftoverSubtitle =>
      'Lưu phần còn lại vào kho (tầng Ăn liền) và đặt nhắc dùng sớm.';

  @override
  String get leftoverServingsLabel => 'Số khẩu phần còn';

  @override
  String servingsCount(int count) {
    return '$count phần';
  }

  @override
  String get leftoverReminderLabel => 'Nhắc dùng';

  @override
  String leftoverReminderInDays(int days) {
    return 'Sau $days ngày';
  }

  @override
  String get leftoverSafetyNote =>
      'Thức ăn đã nấu nên dùng trong 1–2 ngày. Kiểm tra mùi và trạng thái trước khi ăn.';

  @override
  String get leftoverSaveCta => 'Lưu phần thừa';

  @override
  String get leftoverSaved => 'Đã lưu phần thừa vào kho';

  @override
  String get leftoverSaveFailed => 'Không lưu được. Thử lại.';

  @override
  String get cookResultTitle => 'Đã cập nhật kho';

  @override
  String cookResultSaveLeftovers(int count) {
    return 'Lưu $count phần ăn thừa';
  }

  @override
  String get cookResultViewPantry => 'Xem kho';

  @override
  String cookResultWasteKgSuffix(String kg) {
    return ' · tránh bỏ phí ~$kg kg thực phẩm';
  }

  @override
  String get cookResultUsedNearExpiryPrefix => 'Bạn vừa tận dụng ';

  @override
  String cookResultUsedNearExpiryCount(int count) {
    return '$count nguyên liệu cận hạn';
  }

  @override
  String get cookResultChangesHeader => 'THAY ĐỔI TRONG KHO';

  @override
  String cookResultLowStock(String names) {
    return '$names sắp hết';
  }

  @override
  String get commonNotChosen => 'Chưa chọn';

  @override
  String daysCount(int days) {
    return '$days ngày';
  }

  @override
  String daysApprox(int days) {
    return '~$days ngày';
  }

  @override
  String get tierAll => 'Tất cả';

  @override
  String get pantryTitle => 'Kho thực phẩm';

  @override
  String pantrySortPrefix(String label) {
    return 'Sắp xếp: $label';
  }

  @override
  String get pantryAddIngredient => 'Thêm nguyên liệu';

  @override
  String get pantrySearchHint => 'Tìm trong tủ bếp…';

  @override
  String get pantryNoResults => 'Không có kết quả';

  @override
  String get pantryNoResultsBody => 'Thử đổi bộ lọc hoặc từ khóa khác.';

  @override
  String get pantryEmptyTitle => 'Tủ bếp đang trống';

  @override
  String get pantryEmptyBody => 'Thêm nguyên liệu đầu tiên để nhận gợi ý món.';

  @override
  String get pantrySectionNear => 'Cần dùng sớm';

  @override
  String get pantrySectionAll => 'Tất cả';

  @override
  String get pantrySectionRest => 'Còn hạn';

  @override
  String pantryConsumedAll(String name) {
    return 'Đã dùng hết $name';
  }

  @override
  String get pantryUpdateFailed => 'Không cập nhật được. Thử lại.';

  @override
  String get pantryDeleteTitle => 'Xóa nguyên liệu?';

  @override
  String pantryDeleteBody(String name) {
    return '“$name” sẽ bị xóa khỏi kho.';
  }

  @override
  String pantryDeleted(String name) {
    return 'Đã xóa $name';
  }

  @override
  String get pantryDeleteFailed => 'Không xóa được. Thử lại.';

  @override
  String get pantryNotFoundTitle => 'Không tìm thấy nguyên liệu';

  @override
  String get pantryNotFoundBody =>
      'Có thể nó đã được dùng hết hoặc đã xóa khỏi kho.';

  @override
  String get pantryDeleteMenu => 'Xóa khỏi kho';

  @override
  String get pantryStatQuantity => 'Số lượng';

  @override
  String get pantryStatExpiry => 'Hạn dùng';

  @override
  String get pantryStatPrice => 'Giá';

  @override
  String get pantryStatStorage => 'Bảo quản';

  @override
  String get pantryFindDishes => 'Tìm món nấu từ nguyên liệu này';

  @override
  String get pantryDetailLocation => 'Vị trí bảo quản';

  @override
  String get pantryDetailAdded => 'Ngày thêm';

  @override
  String get pantryDetailPacked => 'Ngày đóng gói / mua';

  @override
  String get pantryDetailSource => 'Nguồn nhập';

  @override
  String get pantryDetailShelfRef => 'Bảo quản tham khảo';

  @override
  String get pantryDetailCardTitle => 'Chi tiết';

  @override
  String get pantryAdjust => 'Điều chỉnh';

  @override
  String get pantryConsumeAll => 'Đã dùng hết';

  @override
  String pantryItemUpdated(String name) {
    return 'Đã cập nhật $name';
  }

  @override
  String pantryItemAdded(String name) {
    return 'Đã thêm $name vào kho';
  }

  @override
  String get pantrySaveFailed => 'Không lưu được. Kiểm tra lại thông tin.';

  @override
  String get pantryEditTitle => 'Sửa nguyên liệu';

  @override
  String get pantryAddTitle => 'Thêm nguyên liệu';

  @override
  String get pantryFieldName => 'Tên nguyên liệu';

  @override
  String get pantryFieldNameHint => 'VD: Cà chua bi';

  @override
  String get pantryFieldCategory => 'Nhóm thực phẩm';

  @override
  String get pantryFieldCategoryHint => 'VD: Rau củ';

  @override
  String get pantryFieldStorage => 'Nơi bảo quản';

  @override
  String get pantryFieldExpiry => 'Hạn sử dụng';

  @override
  String get pantryFieldPrice => 'Giá (tùy chọn)';

  @override
  String get pantrySaveChanges => 'Lưu thay đổi';

  @override
  String get pantryAddToPantry => 'Thêm vào kho';

  @override
  String adjustQtyTitle(String name) {
    return 'Cập nhật số lượng — $name';
  }

  @override
  String adjustQtySubtitle(String qty, String tier) {
    return 'Hiện có: $qty · $tier';
  }

  @override
  String get adjustQtyPartial => 'Dùng một phần';

  @override
  String get adjustQtyAll => 'Dùng hết';

  @override
  String get adjustQtyRemaining => 'Còn lại sau khi dùng';

  @override
  String get onbDietTitle => 'Bạn muốn ăn theo hướng nào?';

  @override
  String get onbDietSubtitle =>
      'Dùng để xếp hạng gợi ý món. Có thể đổi bất cứ lúc nào trong Cài đặt.';

  @override
  String get onbLater => 'Để sau';

  @override
  String get onbMethodScan => 'Quét';

  @override
  String get onbMethodVoice => 'Nói';

  @override
  String get onbMethodManual => 'Nhập tay';

  @override
  String get onbPantryTitle => 'Thêm nguyên liệu chỉ trong vài giây';

  @override
  String get onbPantryBody =>
      'Quét tem nhãn hoặc hóa đơn để lấy sẵn tên, khối lượng, hạn dùng. Bận tay thì đọc bằng giọng nói. Không có bao bì thì nhập tay thật nhanh.';

  @override
  String get onbPantryCta => 'Thêm nguyên liệu đầu tiên';

  @override
  String get suggestionsTitle => 'Gợi ý cho bạn';

  @override
  String get suggestionsQuickCook => '≤ 30 phút';

  @override
  String get suggestionsEmptyTitle => 'Chưa đủ nguyên liệu để gợi ý';

  @override
  String get suggestionsEmptyBody =>
      'Thêm vài nguyên liệu vào kho để nhận 3–5 gợi ý món.';

  @override
  String suggestionsCaption(int count) {
    return '$count món hợp nhất với tủ bếp hiện tại · ưu tiên đồ cận hạn';
  }

  @override
  String get suggestionsWhyScore => 'Vì sao điểm này?';

  @override
  String chipUseNearExpiry(int count) {
    return 'Dùng $count đồ cận hạn';
  }

  @override
  String chipAvailable(int percent) {
    return 'Có sẵn $percent%';
  }

  @override
  String chipToBuy(int count) {
    return 'Cần mua $count';
  }

  @override
  String get chipNoBuy => 'Không cần mua';

  @override
  String scoreSheetTitle(String name, int score) {
    return 'Vì sao “$name” đạt $score điểm?';
  }

  @override
  String get scoreFormula => 'Điểm = 0.4·E + 0.3·A + 0.2·P + 0.1·U';

  @override
  String get scoreCompE => 'Dùng đồ cận hạn';

  @override
  String get scoreCompA => 'Tỉ lệ nguyên liệu có sẵn';

  @override
  String get scoreCompP => 'Hợp khẩu phần & sở thích';

  @override
  String get scoreCompU => 'Ít phải mua thêm';

  @override
  String get scoreReasonENone => 'Không dùng nguyên liệu cận hạn nào';

  @override
  String scoreReasonE(int count, String list) {
    return 'Dùng $count nguyên liệu cận hạn: $list';
  }

  @override
  String scoreReasonA(int percent) {
    return '$percent% nguyên liệu đã có trong tủ bếp';
  }

  @override
  String scoreReasonP(int servings, int kcal, int minutes) {
    return '$servings khẩu phần · $kcal kcal · $minutes phút';
  }

  @override
  String get scoreReasonUNone => 'Không phải mua thêm nguyên liệu nào';

  @override
  String scoreReasonU(int count) {
    return 'Chỉ cần mua thêm $count nguyên liệu';
  }

  @override
  String get dishDetailTitle => 'Chi tiết món';

  @override
  String dishIngredientsWithServings(int servings) {
    return 'Nguyên liệu · $servings phần';
  }

  @override
  String get dishSeasonings => 'Gia vị';

  @override
  String get dishHowTo => 'Cách làm';

  @override
  String get dishServingsLabel => 'Khẩu phần';

  @override
  String get dishCookedThis => 'Đã nấu món này';

  @override
  String dishAddedToShopping(int count) {
    return 'Đã thêm $count nguyên liệu vào danh sách mua';
  }

  @override
  String get dishShoppingNotReady =>
      'Danh sách mua chưa sẵn sàng — thử lại sau.';

  @override
  String dishAddMissing(int count) {
    return 'Thêm $count nguyên liệu thiếu vào danh sách mua';
  }

  @override
  String get checklistNearExpiry => 'cận hạn';

  @override
  String get checklistToBuy => 'cần mua';

  @override
  String get macroEstimateNote =>
      'Ước tính theo 1 khẩu phần · nguồn Viện Dinh dưỡng Quốc gia';

  @override
  String ingredientCount(int count) {
    return '$count nguyên liệu';
  }

  @override
  String get seeAll => 'Xem tất cả';

  @override
  String get greetingMorning => 'Chào buổi sáng';

  @override
  String get greetingNoon => 'Chào buổi trưa';

  @override
  String get greetingAfternoon => 'Chào buổi chiều';

  @override
  String get greetingEvening => 'Chào buổi tối';

  @override
  String get homeWhatToEat => 'Hôm nay ăn gì?';

  @override
  String get homeEmptyTitle => 'Kho của bạn đang trống';

  @override
  String get homeEmptyBody =>
      'Thêm vài nguyên liệu để nhận gợi ý món và nhắc hạn sử dụng.';

  @override
  String get homeAddFirst => 'Thêm nguyên liệu đầu tiên';

  @override
  String get homeTileSuggestDish => 'Gợi ý món';

  @override
  String homeSuggestionCount(int count) {
    return '$count món phù hợp';
  }

  @override
  String get homeSuggestFallback => 'Món hợp tủ bếp';

  @override
  String get homeQuickAdd => 'Thêm nhanh';

  @override
  String get homeQuickAddSub => 'Tem · Hóa đơn · Giọng nói';

  @override
  String get homeUseSoon => 'Cần dùng sớm';

  @override
  String get homeNoNearExpiry =>
      'Không có nguyên liệu nào cận hạn. Tủ bếp của bạn rất tươi tốt!';

  @override
  String get homeSuggestionsLoadFail =>
      'Chưa tải được gợi ý. Kéo xuống để làm mới.';

  @override
  String get wdMon => 'T2';

  @override
  String get wdTue => 'T3';

  @override
  String get wdWed => 'T4';

  @override
  String get wdThu => 'T5';

  @override
  String get wdFri => 'T6';

  @override
  String get wdSat => 'T7';

  @override
  String get wdSun => 'CN';

  @override
  String get mealPlanTitle => 'Thực đơn tuần';

  @override
  String get mealPlanGenerateShopping => 'Tạo danh sách mua sắm';

  @override
  String get mealPlanPickDish => 'Chọn món';

  @override
  String get mealPlanPickDishSub => 'Từ gợi ý hợp tủ bếp của bạn';

  @override
  String get mealSlotChosen => 'Món đã chọn';

  @override
  String get mealSlotAdd => '+ Thêm';

  @override
  String get reportsTitle => 'Chống lãng phí';

  @override
  String get reportsEmptyTitle => 'Chưa có dữ liệu';

  @override
  String get reportsEmptyBody =>
      'Nấu vài món dùng nguyên liệu cận hạn để xem bạn tiết kiệm được bao nhiêu.';

  @override
  String get reportsWeeklyCard => 'Nguyên liệu cứu được theo tuần';

  @override
  String get reportsByCategoryCard => 'Theo nhóm thực phẩm';

  @override
  String reportsHeroPeriod(String period) {
    return '$period · nguyên liệu dùng trước hạn';
  }

  @override
  String reportsHeroDetail(String kg, int dishes) {
    return '≈ $kg thực phẩm tránh bị bỏ phí · $dishes món đã nấu';
  }

  @override
  String get prefsTitle => 'Tùy chọn';

  @override
  String get prefsGroupMeal => 'Bữa ăn';

  @override
  String get prefsDietary => 'Ưu tiên dinh dưỡng';

  @override
  String get prefsUnit => 'Đơn vị đo mặc định';

  @override
  String get prefsCurrency => 'Tiền tệ hiển thị';

  @override
  String get prefsCurrencyValue => 'VND (đ)';

  @override
  String get prefsGroupAppearance => 'Giao diện';

  @override
  String get prefsLanguage => 'Ngôn ngữ';

  @override
  String get langVi => 'Tiếng Việt';

  @override
  String get langEn => 'English';

  @override
  String get prefsTheme => 'Chủ đề';

  @override
  String get themeLight => 'Sáng';

  @override
  String get themeDark => 'Tối';

  @override
  String get themeSystem => 'Theo hệ thống';

  @override
  String get catVegetables => 'Rau củ';

  @override
  String get catMeatSeafood => 'Thịt & Hải sản';

  @override
  String get catSpices => 'Gia vị';

  @override
  String get catDairyEgg => 'Trứng & Sữa';

  @override
  String get catDryGoods => 'Đồ khô';

  @override
  String get catOther => 'Khác';

  @override
  String scanSaveError(String error) {
    return 'Lỗi lưu nguyên liệu: $error';
  }

  @override
  String scanAddedToPantry(String name) {
    return 'Đã thêm $name vào kho!';
  }

  @override
  String scanAddedCountToPantry(int count) {
    return 'Đã thêm $count nguyên liệu vào kho!';
  }

  @override
  String get scanNoName => 'Chưa rõ tên';

  @override
  String get scanNeedsCheckShort => 'Kiểm tra';

  @override
  String get scanAddRow => 'Thêm dòng';

  @override
  String get chooserScanLabel => 'Quét tem nhãn';

  @override
  String get chooserScanLabelSub => 'Chụp nhãn cân trên sản phẩm đóng gói';

  @override
  String get chooserScanReceipt => 'Quét hóa đơn';

  @override
  String get chooserScanReceiptSub => 'Chụp hóa đơn, thêm nhiều mục một lúc';

  @override
  String get chooserVoice => 'Nói';

  @override
  String get chooserVoiceSub => 'Đọc tên nguyên liệu và số lượng';

  @override
  String get chooserManual => 'Nhập tay';

  @override
  String get chooserManualSub => 'Tự chọn từ danh mục nguyên liệu';

  @override
  String get camModeLabel => 'Tem nhãn';

  @override
  String get camModeReceipt => 'Hóa đơn';

  @override
  String camScanTitle(String kind) {
    return 'Quét $kind';
  }

  @override
  String get camNoCamera => 'Thiết bị không có máy ảnh.';

  @override
  String camOpenError(String error) {
    return 'Không mở được máy ảnh: $error';
  }

  @override
  String get camNoFlash => 'Đèn flash không khả dụng trên thiết bị này.';

  @override
  String camShootError(String error) {
    return 'Không chụp được: $error';
  }

  @override
  String camGalleryError(String error) {
    return 'Không mở được thư viện ảnh: $error';
  }

  @override
  String get camReading => 'Đang đọc thông tin…';

  @override
  String get camOpening => 'Đang mở máy ảnh…';

  @override
  String get camGuideLabel => 'Đưa nhãn cân vào khung, giữ máy thẳng';

  @override
  String get camGuideReceipt => 'Đưa toàn bộ hóa đơn vào khung';

  @override
  String get camPermissionNeeded => 'Cần quyền máy ảnh để quét trực tiếp.';

  @override
  String get camGrantPermission => 'Cấp quyền máy ảnh';

  @override
  String get camUseGallery => 'Dùng ảnh có sẵn';

  @override
  String get reviewLabelTitle => 'Kiểm tra thông tin';

  @override
  String reviewFieldsRead(int count) {
    return 'Đã đọc được $count trường. Kiểm tra lại trường được đánh dấu trước khi lưu.';
  }

  @override
  String get reviewNetWeight => 'Khối lượng tịnh';

  @override
  String get reviewPackedDate => 'Ngày đóng gói';

  @override
  String get reviewStorageTier => 'Tầng bảo quản';

  @override
  String get reviewCategory => 'Danh mục';

  @override
  String get reviewNameHint => 'Nhập tên nguyên liệu';

  @override
  String get reviewUnit => 'Đơn vị';

  @override
  String get reviewPurchasePrice => 'Giá mua (VNĐ)';

  @override
  String get reviewPriceHint => 'Ví dụ: 18000';

  @override
  String get reviewPickCategory => 'Chọn danh mục';

  @override
  String get reviewLabelPhoto => 'Ảnh tem nhãn';

  @override
  String get reviewRetake => 'Chụp lại';

  @override
  String reviewReceiptTitle(int count) {
    return 'Hóa đơn — $count mục';
  }

  @override
  String reviewSelectedOf(int count) {
    return ' / $count mục được chọn';
  }

  @override
  String get reviewDeselectAll => 'Bỏ chọn tất cả';

  @override
  String get reviewSelectAll => 'Chọn tất cả';

  @override
  String reviewAddCount(int count) {
    return 'Thêm $count mục vào kho';
  }

  @override
  String get reviewPickAtLeastOne => 'Chọn ít nhất 1 mục';

  @override
  String get reviewEditItem => 'Chỉnh sửa nguyên liệu';

  @override
  String get reviewRemoveItem => 'Xóa mục này';

  @override
  String get voiceCaptureTitle => 'Nói để thêm';

  @override
  String get voiceCapturePrompt => 'Đọc tên nguyên liệu và số lượng';

  @override
  String get voiceCaptureExample =>
      'VD: “2 lạng thịt bò, 1 bó cải bó xôi, 3 quả trứng”';

  @override
  String get voiceListening => 'Đang nghe…';

  @override
  String get voiceMicOff => 'Chưa bật được micro — cứ đọc rồi kiểm tra';

  @override
  String get voiceStopReview => 'Dừng & Kiểm tra';

  @override
  String get voiceReviewTitle => 'Kiểm tra kết quả';

  @override
  String get voiceRerecord => 'Ghi lại';

  @override
  String voiceParsedCount(int count) {
    return 'Đã bóc tách $count nguyên liệu';
  }

  @override
  String voiceAddCount(int count) {
    return 'Thêm $count nguyên liệu';
  }

  @override
  String get scanFailLabelTitle => 'Không đọc được nhãn';

  @override
  String get scanFailReceiptTitle => 'Không đọc được hóa đơn';

  @override
  String get scanFailVoiceTitle => 'Không nghe rõ';

  @override
  String get scanFailVoiceReason1 => 'Môi trường quá ồn';

  @override
  String get scanFailVoiceReason2 => 'Nói quá nhanh hoặc quá nhỏ';

  @override
  String get scanFailVoiceReason3 => 'Micro bị che';

  @override
  String get scanFailImgReason1 => 'Ảnh bị mờ hoặc chụp nghiêng';

  @override
  String get scanFailImgReason2 => 'Nhãn bị rách hoặc phai mực';

  @override
  String get scanFailImgReason3 => 'Thiếu sáng khi chụp';

  @override
  String get scanFailRerecord => 'Thu lại';

  @override
  String featureComingInMilestone(String milestone) {
    return 'Sẽ hiện thực ở $milestone';
  }

  @override
  String get authSignIn => 'Đăng nhập';

  @override
  String get authSignUp => 'Đăng ký';

  @override
  String get authCreateAccount => 'Tạo tài khoản';

  @override
  String get authEmail => 'Email';

  @override
  String get authPassword => 'Mật khẩu';

  @override
  String get authFullName => 'Họ và tên';

  @override
  String get authFullNameHint => 'Nguyễn Văn A';

  @override
  String get authPasswordHint => 'Ít nhất 8 ký tự';

  @override
  String get authForgotQ => 'Quên mật khẩu?';

  @override
  String get authForgotTitle => 'Quên mật khẩu';

  @override
  String get authInvalidEmail => 'Email không hợp lệ';

  @override
  String get authEnterPassword => 'Nhập mật khẩu';

  @override
  String get authEnterName => 'Nhập họ và tên';

  @override
  String get authPasswordTooShort => 'Ít nhất 8 ký tự';

  @override
  String get authPhone => 'Số điện thoại';

  @override
  String get authInvalidPhone => 'Số điện thoại không hợp lệ';

  @override
  String get authOtpTitle => 'Nhập mã xác thực';

  @override
  String authOtpSubtitle(String phone) {
    return 'Mã gồm 6 chữ số đã được gửi tới $phone.';
  }

  @override
  String get authOtpLabel => 'Mã xác thực';

  @override
  String get authOtpInvalid => 'Mã gồm 6 chữ số';

  @override
  String get authOtpConfirm => 'Xác nhận';

  @override
  String get authOtpResendCta => 'Gửi lại mã';

  @override
  String get authOtpResent => 'Đã gửi lại mã.';

  @override
  String get authOtpMissingArgs => 'Thiếu thông tin. Quay lại và thử lại.';

  @override
  String get welcomeSlide1Title => 'Biến nguyên liệu đang có thành bữa ăn';

  @override
  String get welcomeSlide1Body =>
      'SweepFood theo dõi hạn dùng và luôn đẩy những món cần dùng sớm lên đầu.';

  @override
  String get welcomeSlide2Title => 'Gợi ý món hợp tủ bếp của bạn';

  @override
  String get welcomeSlide2Body =>
      '3–5 món mỗi lần, chấm điểm theo nguyên liệu sẵn có và đồ sắp hết hạn.';

  @override
  String get welcomeSlide3Title => 'Nấu hết đồ, bớt lãng phí';

  @override
  String get welcomeSlide3Body =>
      'Xem bạn đã dùng kịp bao nhiêu nguyên liệu trước hạn — tính bằng kg tránh bỏ phí.';

  @override
  String get welcomeStart => 'Bắt đầu';

  @override
  String get welcomeHaveAccount => 'Đã có tài khoản? Đăng nhập';

  @override
  String get loginSubtitle => 'Tiếp tục quản lý tủ bếp của bạn';

  @override
  String get loginNoAccount => 'Chưa có tài khoản? ';

  @override
  String get loginFailed => 'Đăng nhập không thành công. Thử lại nhé.';

  @override
  String get registerSubtitle => 'Bắt đầu tiết kiệm thực phẩm cùng SweepFood';

  @override
  String get registerHaveAccount => 'Đã có tài khoản? ';

  @override
  String get registerNeedTerms => 'Cần đồng ý với Điều khoản để tiếp tục.';

  @override
  String get termsPrefix => 'Tôi đồng ý với ';

  @override
  String get termsOfUse => 'Điều khoản sử dụng';

  @override
  String get termsAnd => ' và ';

  @override
  String get termsPrivacy => 'Chính sách bảo mật';

  @override
  String get forgotSubtitle =>
      'Nhập số điện thoại tài khoản, chúng tôi sẽ gửi mã đặt lại mật khẩu.';

  @override
  String get forgotSendLink => 'Gửi liên kết';

  @override
  String get forgotSendCode => 'Gửi mã';

  @override
  String get forgotBackToLogin => 'Quay lại đăng nhập';

  @override
  String get resetPasswordTitle => 'Đặt lại mật khẩu';

  @override
  String resetPasswordSubtitle(String phone) {
    return 'Nhập mã đã gửi tới $phone và mật khẩu mới.';
  }

  @override
  String get resetPasswordNewLabel => 'Mật khẩu mới';

  @override
  String get resetPasswordCta => 'Đặt lại mật khẩu';

  @override
  String get resetPasswordDone => 'Đã đặt lại mật khẩu. Đăng nhập lại nhé.';

  @override
  String forgotSentTo(String email) {
    return 'Đã gửi tới $email';
  }

  @override
  String get forgotCheckInbox =>
      'Kiểm tra hộp thư (kể cả mục spam). Liên kết hiệu lực trong 30 phút.';

  @override
  String get commonYou => 'Bạn';

  @override
  String get dayToday => 'Hôm nay';

  @override
  String get dayYesterday => 'Hôm qua';

  @override
  String get willOpenInBrowser => 'Sẽ mở trong trình duyệt.';

  @override
  String get notifTitle => 'Thông báo';

  @override
  String get notifMarkAllRead => 'Đánh dấu đã đọc';

  @override
  String get notifEmptyTitle => 'Chưa có thông báo';

  @override
  String get notifEmptyBody =>
      'Nhắc hạn sử dụng và tổng kết chống lãng phí sẽ xuất hiện ở đây.';

  @override
  String get nearExpiryNotFound => 'Không tìm thấy nguyên liệu này trong kho.';

  @override
  String get nearExpiryMarkUsed => 'Đánh dấu đã dùng';

  @override
  String get nearExpirySeeSuggestions => 'Xem gợi ý';

  @override
  String get expiryTipVeg =>
      'Rau ăn lá nên dùng trong ngày để giữ độ tươi và dinh dưỡng. Kiểm tra lá có bị úa hoặc nhũn không trước khi nấu.';

  @override
  String get expiryTipFruit =>
      'Trái cây chín nhanh ở nhiệt độ phòng. Cho vào ngăn mát để giữ thêm 2–3 ngày; dùng ngay khi vỏ bắt đầu nhăn.';

  @override
  String get expiryTipMeat =>
      'Thịt tươi để ngăn mát nên nấu trong 1–2 ngày. Nếu chưa dùng kịp, cấp đông ngay để giữ chất lượng.';

  @override
  String get expiryTipFish =>
      'Cá và hải sản rất nhanh hỏng — nấu trong ngày hoặc cấp đông. Ngửi thấy mùi tanh gắt thì nên bỏ.';

  @override
  String get expiryTipDairy =>
      'Sữa và chế phẩm từ sữa giữ trong ngăn mát dưới 4°C. Dùng trước hạn và kiểm tra mùi trước khi uống.';

  @override
  String get expiryTipEgg =>
      'Trứng để ngăn mát dùng tốt trong vài tuần. Thử thả vào nước: trứng nổi là đã cũ.';

  @override
  String get expiryTipDefault =>
      'Ưu tiên dùng nguyên liệu này sớm. Luôn kiểm tra màu sắc, mùi và trạng thái thực phẩm trước khi chế biến.';

  @override
  String get settingsGroupAccount => 'Tài khoản';

  @override
  String get settingsProfilePassword => 'Hồ sơ & mật khẩu';

  @override
  String get settingsPlan => 'Gói dịch vụ';

  @override
  String get settingsPremiumSoon => 'Premium sắp có';

  @override
  String get settingsPantrySharing => 'Chia sẻ tủ bếp';

  @override
  String get settingsGroupMealPlanning => 'Kế hoạch bữa ăn';

  @override
  String get settingsWasteReport => 'Báo cáo chống lãng phí';

  @override
  String get settingsGroupApp => 'Ứng dụng';

  @override
  String get settingsGroupOther => 'Khác';

  @override
  String get settingsAboutData => 'Giới thiệu & nguồn dữ liệu';

  @override
  String get settingsSignOut => 'Đăng xuất';

  @override
  String get signOutConfirmTitle => 'Đăng xuất?';

  @override
  String get signOutConfirmBody =>
      'Bạn sẽ cần đăng nhập lại để dùng SweepFood.';

  @override
  String get planFullFree => 'Bản đầy đủ · miễn phí';

  @override
  String get planPremiumDeveloping =>
      'Premium (đồng bộ, báo cáo nâng cao…) đang phát triển';

  @override
  String get planInterested => 'Quan tâm';

  @override
  String get aboutTitle => 'Giới thiệu & dữ liệu';

  @override
  String get aboutVersion => 'Phiên bản 1.0.0 (MVP)';

  @override
  String get aboutDataSources => 'Nguồn dữ liệu';

  @override
  String get aboutNutritionData => 'Giá trị dinh dưỡng thực phẩm';

  @override
  String get aboutNutritionSource => 'Viện Dinh dưỡng QG';

  @override
  String get aboutShelfLifeData => 'Thời gian bảo quản tham khảo';

  @override
  String get aboutDisclaimer =>
      'Thông tin dinh dưỡng và thời gian bảo quản chỉ mang tính ước tính, không thay thế tư vấn của chuyên gia dinh dưỡng hoặc y tế. Luôn kiểm tra màu sắc, mùi và trạng thái thực phẩm trước khi sử dụng.';

  @override
  String get aboutRateApp => 'Đánh giá ứng dụng';

  @override
  String get aboutThanks => 'Cảm ơn bạn!';

  @override
  String get notifSettingsTypesHeader => 'LOẠI THÔNG BÁO';

  @override
  String get notifTypeNearExpiry => 'Cảnh báo cận hạn';

  @override
  String get notifTypeNearExpirySub => 'Khi nguyên liệu sắp hết hạn';

  @override
  String get notifTypeDailySuggestions => 'Gợi ý món hằng ngày';

  @override
  String get notifTypeWeeklyReport => 'Báo cáo tuần';

  @override
  String get notifTypePostCook => 'Nhắc sau khi nấu';

  @override
  String get notifTypePromos => 'Khuyến mãi & mẹo';

  @override
  String get notifSettingsTiming => 'Thời điểm';

  @override
  String get notifRemindAt => 'Nhắc cận hạn lúc';

  @override
  String get notifDnd => 'Không làm phiền';

  @override
  String get notifDndStart => 'Bắt đầu không làm phiền';

  @override
  String get notifDndEnd => 'Kết thúc không làm phiền';

  @override
  String get pantrySharingIntro =>
      'Mời tối đa 4 người cùng xem và cập nhật tủ bếp. Mọi thay đổi được đồng bộ cho tất cả thành viên.';

  @override
  String get pantrySharingFootnote =>
      'Thành viên có thể thêm, sửa, xóa nguyên liệu và xem gợi ý món. Chỉ chủ tủ bếp mới xóa được thành viên.';

  @override
  String get pantrySharingInvite => 'Mời thành viên';

  @override
  String get pantryMemberInvited => 'Đã mời · chờ xác nhận';

  @override
  String get pantryRoleOwner => 'Chủ tủ bếp';

  @override
  String get pantryRoleEditor => 'Có thể chỉnh sửa';

  @override
  String get profileGroupInfo => 'Thông tin';

  @override
  String get profileEditSoon => 'Sửa hồ sơ sẽ có ở bản sau.';

  @override
  String get profileGroupSecurity => 'Bảo mật';

  @override
  String get profileChangePassword => 'Đổi mật khẩu';

  @override
  String get profileChangePasswordSoon => 'Đổi mật khẩu sẽ có ở bản sau.';

  @override
  String get profileDeleteAccount => 'Xóa tài khoản';

  @override
  String get profileDeleteConfirmTitle => 'Xóa tài khoản?';

  @override
  String get profileDeleteConfirmBody =>
      'Toàn bộ dữ liệu tủ bếp sẽ bị xóa vĩnh viễn. Hành động này không thể hoàn tác.';

  @override
  String get profileDeleteRequested =>
      'Yêu cầu xóa tài khoản đã được ghi nhận.';

  @override
  String minutesLabel(int minutes) {
    return '$minutes phút';
  }

  @override
  String dishMetaPrep(int minutes) {
    return '$minutes phút chuẩn bị';
  }

  @override
  String dishMetaKcalPerServing(int kcal) {
    return '$kcal kcal / khẩu phần';
  }

  @override
  String get shoppingTitle => 'Danh sách mua sắm';

  @override
  String get shoppingAddItem => 'Thêm món';

  @override
  String get shoppingEmptyTitle => 'Chưa có danh sách mua sắm';

  @override
  String get shoppingEmptyBody =>
      'Lập thực đơn tuần rồi tạo danh sách mua sắm chỉ với 1 chạm.';

  @override
  String get shoppingPlanWeek => 'Lập thực đơn tuần';

  @override
  String get shoppingShowInStock => 'Hiện nguyên liệu đã có trong kho';

  @override
  String get shoppingEstimate => 'Ước tính';

  @override
  String shoppingToBuyCount(int count) {
    return '$count nguyên liệu cần mua';
  }

  @override
  String get shoppingItemName => 'Tên món';

  @override
  String get shoppingCategoryOptional => 'Danh mục (tùy chọn)';

  @override
  String get shoppingCategoryHint => 'Rau củ, Thịt & hải sản, …';

  @override
  String get shoppingAddToList => 'Thêm vào danh sách';

  @override
  String get shoppingHavePill => 'đã có';

  @override
  String get shoppingFromRecipe => 'Từ công thức';

  @override
  String get subCurrentPlan => 'Bạn đang dùng';

  @override
  String get subInterestRegistered => 'Đã đăng ký quan tâm Premium';

  @override
  String get subInterestCta => 'Quan tâm Premium — báo tôi khi ra mắt';

  @override
  String get subDisclaimer =>
      'Trong giai đoạn thử nghiệm, tất cả tính năng đang miễn phí. Sau này một số tính năng nâng cao (đồng bộ nhiều thiết bị, chia sẻ tủ bếp, báo cáo chi tiết) sẽ chuyển sang gói Premium — bạn sẽ được báo trước.';

  @override
  String get subTierFree => 'Bản đầy đủ · miễn phí';

  @override
  String get subTierMonthly => 'Premium tháng';

  @override
  String get subTierYearly => 'Premium năm';

  @override
  String get subTierFamily => 'Premium gia đình';

  @override
  String get paywallTitle => 'SweepFood Premium sắp ra mắt';

  @override
  String get paywallSubtitle =>
      'Hiện tại bạn đang dùng miễn phí tất cả tính năng. Đăng ký để được báo khi Premium chính thức và nhận ưu đãi sớm.';

  @override
  String get paywallBenefit1 => 'Kho nguyên liệu không giới hạn';

  @override
  String get paywallBenefit2 => 'Quét tem & hóa đơn không giới hạn';

  @override
  String get paywallBenefit3 => 'Lập thực đơn tuần & danh sách mua sắm';

  @override
  String get paywallBenefit4 => 'Mục tiêu dinh dưỡng theo ngày';

  @override
  String get paywallBenefit5 => 'Báo cáo thực phẩm đã tiết kiệm';

  @override
  String get paywallBenefit6 => 'Chia sẻ tủ bếp cho tối đa 4 người';

  @override
  String get paywallSubmitted => 'Đã ghi nhận — cảm ơn bạn!';

  @override
  String get paywallNotifyMe => 'Nhận thông báo khi ra mắt';

  @override
  String get paywallFinePrint =>
      'Chưa tính phí · giá & gói đang trong giai đoạn kiểm chứng';
}
