import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_vi.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppL10n
/// returned by `AppL10n.of(context)`.
///
/// Applications need to include `AppL10n.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppL10n.localizationsDelegates,
///   supportedLocales: AppL10n.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppL10n.supportedLocales
/// property.
abstract class AppL10n {
  AppL10n(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppL10n of(BuildContext context) {
    return Localizations.of<AppL10n>(context, AppL10n)!;
  }

  static const LocalizationsDelegate<AppL10n> delegate = _AppL10nDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('vi'),
  ];

  /// No description provided for @appName.
  ///
  /// In vi, this message translates to:
  /// **'SweepFood'**
  String get appName;

  /// No description provided for @navHome.
  ///
  /// In vi, this message translates to:
  /// **'Trang chủ'**
  String get navHome;

  /// No description provided for @navPantry.
  ///
  /// In vi, this message translates to:
  /// **'Kho'**
  String get navPantry;

  /// No description provided for @navSuggestions.
  ///
  /// In vi, this message translates to:
  /// **'Gợi ý'**
  String get navSuggestions;

  /// No description provided for @navShopping.
  ///
  /// In vi, this message translates to:
  /// **'Mua sắm'**
  String get navShopping;

  /// No description provided for @navProfile.
  ///
  /// In vi, this message translates to:
  /// **'Cá nhân'**
  String get navProfile;

  /// No description provided for @commonRetry.
  ///
  /// In vi, this message translates to:
  /// **'Thử lại'**
  String get commonRetry;

  /// No description provided for @commonUndo.
  ///
  /// In vi, this message translates to:
  /// **'Hoàn tác'**
  String get commonUndo;

  /// No description provided for @commonRecommended.
  ///
  /// In vi, this message translates to:
  /// **'Gợi ý'**
  String get commonRecommended;

  /// No description provided for @commonAllow.
  ///
  /// In vi, this message translates to:
  /// **'Cho phép'**
  String get commonAllow;

  /// No description provided for @commonNotNow.
  ///
  /// In vi, this message translates to:
  /// **'Không phải bây giờ'**
  String get commonNotNow;

  /// No description provided for @commonCancel.
  ///
  /// In vi, this message translates to:
  /// **'Hủy'**
  String get commonCancel;

  /// No description provided for @commonSave.
  ///
  /// In vi, this message translates to:
  /// **'Lưu'**
  String get commonSave;

  /// No description provided for @commonDone.
  ///
  /// In vi, this message translates to:
  /// **'Xong'**
  String get commonDone;

  /// No description provided for @commonClose.
  ///
  /// In vi, this message translates to:
  /// **'Đóng'**
  String get commonClose;

  /// No description provided for @commonDelete.
  ///
  /// In vi, this message translates to:
  /// **'Xoá'**
  String get commonDelete;

  /// No description provided for @commonEdit.
  ///
  /// In vi, this message translates to:
  /// **'Sửa'**
  String get commonEdit;

  /// No description provided for @commonContinue.
  ///
  /// In vi, this message translates to:
  /// **'Tiếp tục'**
  String get commonContinue;

  /// No description provided for @commonSkip.
  ///
  /// In vi, this message translates to:
  /// **'Bỏ qua'**
  String get commonSkip;

  /// No description provided for @commonComingSoon.
  ///
  /// In vi, this message translates to:
  /// **'Sắp có'**
  String get commonComingSoon;

  /// No description provided for @tierEatSoon.
  ///
  /// In vi, this message translates to:
  /// **'Ăn liền / Nấu trong ngày'**
  String get tierEatSoon;

  /// No description provided for @tierEatSoonShort.
  ///
  /// In vi, this message translates to:
  /// **'Ăn liền'**
  String get tierEatSoonShort;

  /// No description provided for @tierFridge.
  ///
  /// In vi, this message translates to:
  /// **'Ngăn mát'**
  String get tierFridge;

  /// No description provided for @tierFreezer.
  ///
  /// In vi, this message translates to:
  /// **'Ngăn đông'**
  String get tierFreezer;

  /// No description provided for @tierPantryShelf.
  ///
  /// In vi, this message translates to:
  /// **'Kệ đồ khô'**
  String get tierPantryShelf;

  /// No description provided for @pantrySortPriority.
  ///
  /// In vi, this message translates to:
  /// **'Cận hạn'**
  String get pantrySortPriority;

  /// No description provided for @pantrySortName.
  ///
  /// In vi, this message translates to:
  /// **'Tên A–Z'**
  String get pantrySortName;

  /// No description provided for @pantrySortRecent.
  ///
  /// In vi, this message translates to:
  /// **'Mới thêm'**
  String get pantrySortRecent;

  /// No description provided for @pantrySourceLabelScan.
  ///
  /// In vi, this message translates to:
  /// **'Quét tem nhãn'**
  String get pantrySourceLabelScan;

  /// No description provided for @pantrySourceReceiptScan.
  ///
  /// In vi, this message translates to:
  /// **'Quét hóa đơn'**
  String get pantrySourceReceiptScan;

  /// No description provided for @pantrySourceVoice.
  ///
  /// In vi, this message translates to:
  /// **'Nhập bằng giọng nói'**
  String get pantrySourceVoice;

  /// No description provided for @pantrySourceManual.
  ///
  /// In vi, this message translates to:
  /// **'Nhập tay'**
  String get pantrySourceManual;

  /// No description provided for @pantrySourceCooked.
  ///
  /// In vi, this message translates to:
  /// **'Thức ăn đã nấu'**
  String get pantrySourceCooked;

  /// No description provided for @cookModeExact.
  ///
  /// In vi, this message translates to:
  /// **'Dùng đúng định lượng'**
  String get cookModeExact;

  /// No description provided for @cookModeExactDesc.
  ///
  /// In vi, this message translates to:
  /// **'Trừ kho theo công thức'**
  String get cookModeExactDesc;

  /// No description provided for @cookModeHalf.
  ///
  /// In vi, this message translates to:
  /// **'Dùng một nửa'**
  String get cookModeHalf;

  /// No description provided for @cookModeHalfDesc.
  ///
  /// In vi, this message translates to:
  /// **'Trừ 50% lượng dự kiến'**
  String get cookModeHalfDesc;

  /// No description provided for @cookModeAll.
  ///
  /// In vi, this message translates to:
  /// **'Dùng hết những gì đang có'**
  String get cookModeAll;

  /// No description provided for @cookModeAllDesc.
  ///
  /// In vi, this message translates to:
  /// **'Đưa các nguyên liệu này về 0'**
  String get cookModeAllDesc;

  /// No description provided for @cookModeCustom.
  ///
  /// In vi, this message translates to:
  /// **'Tự điều chỉnh'**
  String get cookModeCustom;

  /// No description provided for @cookModeCustomDesc.
  ///
  /// In vi, this message translates to:
  /// **'Chỉnh từng nguyên liệu'**
  String get cookModeCustomDesc;

  /// No description provided for @mealSlotBreakfast.
  ///
  /// In vi, this message translates to:
  /// **'Sáng'**
  String get mealSlotBreakfast;

  /// No description provided for @mealSlotLunch.
  ///
  /// In vi, this message translates to:
  /// **'Trưa'**
  String get mealSlotLunch;

  /// No description provided for @mealSlotDinner.
  ///
  /// In vi, this message translates to:
  /// **'Tối'**
  String get mealSlotDinner;

  /// No description provided for @mealSlotSnack.
  ///
  /// In vi, this message translates to:
  /// **'Ăn vặt'**
  String get mealSlotSnack;

  /// No description provided for @mealTypeBreakfast.
  ///
  /// In vi, this message translates to:
  /// **'Bữa sáng'**
  String get mealTypeBreakfast;

  /// No description provided for @mealTypeLunch.
  ///
  /// In vi, this message translates to:
  /// **'Bữa trưa'**
  String get mealTypeLunch;

  /// No description provided for @mealTypeDinner.
  ///
  /// In vi, this message translates to:
  /// **'Bữa tối'**
  String get mealTypeDinner;

  /// No description provided for @reportPeriodWeek.
  ///
  /// In vi, this message translates to:
  /// **'Tuần này'**
  String get reportPeriodWeek;

  /// No description provided for @reportPeriodMonth.
  ///
  /// In vi, this message translates to:
  /// **'Tháng này'**
  String get reportPeriodMonth;

  /// No description provided for @dietBalanced.
  ///
  /// In vi, this message translates to:
  /// **'Cân bằng'**
  String get dietBalanced;

  /// No description provided for @dietBalancedDesc.
  ///
  /// In vi, this message translates to:
  /// **'Đủ nhóm chất, không thiên lệch'**
  String get dietBalancedDesc;

  /// No description provided for @dietHighProtein.
  ///
  /// In vi, this message translates to:
  /// **'Nhiều protein'**
  String get dietHighProtein;

  /// No description provided for @dietHighProteinDesc.
  ///
  /// In vi, this message translates to:
  /// **'Ưu tiên thịt, cá, trứng, đậu'**
  String get dietHighProteinDesc;

  /// No description provided for @dietLowCalorie.
  ///
  /// In vi, this message translates to:
  /// **'Ít năng lượng'**
  String get dietLowCalorie;

  /// No description provided for @dietLowCalorieDesc.
  ///
  /// In vi, this message translates to:
  /// **'Ưu tiên món dưới 400 kcal / khẩu phần'**
  String get dietLowCalorieDesc;

  /// No description provided for @dietMoreVeg.
  ///
  /// In vi, this message translates to:
  /// **'Nhiều rau'**
  String get dietMoreVeg;

  /// No description provided for @dietMoreVegDesc.
  ///
  /// In vi, this message translates to:
  /// **'Ưu tiên món giàu rau củ, chất xơ'**
  String get dietMoreVegDesc;

  /// No description provided for @macroEnergy.
  ///
  /// In vi, this message translates to:
  /// **'Năng lượng'**
  String get macroEnergy;

  /// No description provided for @macroProtein.
  ///
  /// In vi, this message translates to:
  /// **'Đạm'**
  String get macroProtein;

  /// No description provided for @macroCarb.
  ///
  /// In vi, this message translates to:
  /// **'Tinh bột'**
  String get macroCarb;

  /// No description provided for @macroFat.
  ///
  /// In vi, this message translates to:
  /// **'Chất béo'**
  String get macroFat;

  /// No description provided for @macroKcal.
  ///
  /// In vi, this message translates to:
  /// **'{kcal} kcal'**
  String macroKcal(int kcal);

  /// No description provided for @macroGrams.
  ///
  /// In vi, this message translates to:
  /// **'{grams}g'**
  String macroGrams(int grams);

  /// No description provided for @scoreBadgeLabel.
  ///
  /// In vi, this message translates to:
  /// **'ĐIỂM'**
  String get scoreBadgeLabel;

  /// No description provided for @confidenceNeedsReview.
  ///
  /// In vi, this message translates to:
  /// **'Cần kiểm tra'**
  String get confidenceNeedsReview;

  /// No description provided for @wastePillPeriodThisMonth.
  ///
  /// In vi, this message translates to:
  /// **'tháng này'**
  String get wastePillPeriodThisMonth;

  /// No description provided for @wastePillCount.
  ///
  /// In vi, this message translates to:
  /// **'{count} nguyên liệu'**
  String wastePillCount(int count);

  /// No description provided for @wastePillUsedBeforeExpiry.
  ///
  /// In vi, this message translates to:
  /// **'\nđã dùng trước hạn {period}'**
  String wastePillUsedBeforeExpiry(String period);

  /// No description provided for @wastePillUsedBeforeExpiryWithKg.
  ///
  /// In vi, this message translates to:
  /// **'\nđã dùng trước hạn {period} · ≈ {kg} kg tránh bỏ phí'**
  String wastePillUsedBeforeExpiryWithKg(String period, String kg);

  /// No description provided for @expiryNone.
  ///
  /// In vi, this message translates to:
  /// **'Không có hạn'**
  String get expiryNone;

  /// No description provided for @expiryOverdueDays.
  ///
  /// In vi, this message translates to:
  /// **'Quá hạn {days} ngày'**
  String expiryOverdueDays(int days);

  /// No description provided for @expiryToday.
  ///
  /// In vi, this message translates to:
  /// **'Hôm nay'**
  String get expiryToday;

  /// No description provided for @expiryInDays.
  ///
  /// In vi, this message translates to:
  /// **'Còn {days} ngày'**
  String expiryInDays(int days);

  /// No description provided for @expiryInMonths.
  ///
  /// In vi, this message translates to:
  /// **'Còn {months} tháng'**
  String expiryInMonths(int months);

  /// No description provided for @expiryInYears.
  ///
  /// In vi, this message translates to:
  /// **'Còn {years} năm'**
  String expiryInYears(int years);

  /// No description provided for @failNetwork.
  ///
  /// In vi, this message translates to:
  /// **'Không có kết nối mạng. Kiểm tra lại và thử lại.'**
  String get failNetwork;

  /// No description provided for @failTimeout.
  ///
  /// In vi, this message translates to:
  /// **'Máy chủ phản hồi quá lâu. Vui lòng thử lại.'**
  String get failTimeout;

  /// No description provided for @failUnauthorized.
  ///
  /// In vi, this message translates to:
  /// **'Phiên đăng nhập đã hết hạn. Đăng nhập lại nhé.'**
  String get failUnauthorized;

  /// No description provided for @failForbidden.
  ///
  /// In vi, this message translates to:
  /// **'Bạn không có quyền thực hiện thao tác này.'**
  String get failForbidden;

  /// No description provided for @failQuota.
  ///
  /// In vi, this message translates to:
  /// **'Bạn đã dùng hết lượt cho tính năng này trong tháng.'**
  String get failQuota;

  /// No description provided for @failParse.
  ///
  /// In vi, this message translates to:
  /// **'Dữ liệu trả về không đúng định dạng.'**
  String get failParse;

  /// No description provided for @failUnknown.
  ///
  /// In vi, this message translates to:
  /// **'Đã xảy ra lỗi không mong muốn.'**
  String get failUnknown;

  /// No description provided for @permCameraTitle.
  ///
  /// In vi, this message translates to:
  /// **'Cho phép dùng máy ảnh'**
  String get permCameraTitle;

  /// No description provided for @permMicTitle.
  ///
  /// In vi, this message translates to:
  /// **'Cho phép dùng micro'**
  String get permMicTitle;

  /// No description provided for @permCameraDesc.
  ///
  /// In vi, this message translates to:
  /// **'SweepFood cần máy ảnh để quét tem nhãn và hóa đơn. Ảnh chỉ dùng để trích xuất thông tin nguyên liệu, không lưu lại nếu bạn không xác nhận.'**
  String get permCameraDesc;

  /// No description provided for @permMicDesc.
  ///
  /// In vi, this message translates to:
  /// **'SweepFood cần micro để nhận diện giọng nói khi bạn đọc danh sách nguyên liệu. Âm thanh chỉ được xử lý để bóc tách thông tin.'**
  String get permMicDesc;

  /// No description provided for @permCameraSettingsHint.
  ///
  /// In vi, this message translates to:
  /// **'Hãy bật quyền Máy ảnh trong Cài đặt để quét.'**
  String get permCameraSettingsHint;

  /// No description provided for @permMicSettingsHint.
  ///
  /// In vi, this message translates to:
  /// **'Hãy bật quyền Micro trong Cài đặt để nói.'**
  String get permMicSettingsHint;

  /// No description provided for @permCameraRetryHint.
  ///
  /// In vi, this message translates to:
  /// **'Chưa cấp quyền Máy ảnh — hãy thử lại và chọn \"Cho phép\".'**
  String get permCameraRetryHint;

  /// No description provided for @permMicRetryHint.
  ///
  /// In vi, this message translates to:
  /// **'Chưa cấp quyền Micro — hãy thử lại và chọn \"Cho phép\".'**
  String get permMicRetryHint;

  /// No description provided for @permOpenSettings.
  ///
  /// In vi, this message translates to:
  /// **'Mở Cài đặt'**
  String get permOpenSettings;

  /// No description provided for @permFinePrint.
  ///
  /// In vi, this message translates to:
  /// **'Bạn có thể đổi trong Cài đặt bất cứ lúc nào.'**
  String get permFinePrint;

  /// No description provided for @commonConfirm.
  ///
  /// In vi, this message translates to:
  /// **'Xác nhận'**
  String get commonConfirm;

  /// No description provided for @commonBuyShort.
  ///
  /// In vi, this message translates to:
  /// **'+ Mua'**
  String get commonBuyShort;

  /// No description provided for @cookUpdateFailed.
  ///
  /// In vi, this message translates to:
  /// **'Không cập nhật được kho. Thử lại.'**
  String get cookUpdateFailed;

  /// No description provided for @cookConfirmTitle.
  ///
  /// In vi, this message translates to:
  /// **'Bạn đã nấu “{name}”?'**
  String cookConfirmTitle(String name);

  /// No description provided for @cookConfirmSubtitle.
  ///
  /// In vi, this message translates to:
  /// **'Chọn lượng nguyên liệu đã dùng để cập nhật kho'**
  String get cookConfirmSubtitle;

  /// No description provided for @cookExactWithServings.
  ///
  /// In vi, this message translates to:
  /// **'Trừ kho theo công thức ({servings} phần)'**
  String cookExactWithServings(int servings);

  /// No description provided for @customUsageTitle.
  ///
  /// In vi, this message translates to:
  /// **'Điều chỉnh lượng đã dùng'**
  String get customUsageTitle;

  /// No description provided for @leftoverTitle.
  ///
  /// In vi, this message translates to:
  /// **'Còn dư món ăn?'**
  String get leftoverTitle;

  /// No description provided for @leftoverSubtitle.
  ///
  /// In vi, this message translates to:
  /// **'Lưu phần còn lại vào kho (tầng Ăn liền) và đặt nhắc dùng sớm.'**
  String get leftoverSubtitle;

  /// No description provided for @leftoverServingsLabel.
  ///
  /// In vi, this message translates to:
  /// **'Số khẩu phần còn'**
  String get leftoverServingsLabel;

  /// No description provided for @servingsCount.
  ///
  /// In vi, this message translates to:
  /// **'{count} phần'**
  String servingsCount(int count);

  /// No description provided for @leftoverReminderLabel.
  ///
  /// In vi, this message translates to:
  /// **'Nhắc dùng'**
  String get leftoverReminderLabel;

  /// No description provided for @leftoverReminderInDays.
  ///
  /// In vi, this message translates to:
  /// **'Sau {days} ngày'**
  String leftoverReminderInDays(int days);

  /// No description provided for @leftoverSafetyNote.
  ///
  /// In vi, this message translates to:
  /// **'Thức ăn đã nấu nên dùng trong 1–2 ngày. Kiểm tra mùi và trạng thái trước khi ăn.'**
  String get leftoverSafetyNote;

  /// No description provided for @leftoverSaveCta.
  ///
  /// In vi, this message translates to:
  /// **'Lưu phần thừa'**
  String get leftoverSaveCta;

  /// No description provided for @leftoverSaved.
  ///
  /// In vi, this message translates to:
  /// **'Đã lưu phần thừa vào kho'**
  String get leftoverSaved;

  /// No description provided for @leftoverSaveFailed.
  ///
  /// In vi, this message translates to:
  /// **'Không lưu được. Thử lại.'**
  String get leftoverSaveFailed;

  /// No description provided for @cookResultTitle.
  ///
  /// In vi, this message translates to:
  /// **'Đã cập nhật kho'**
  String get cookResultTitle;

  /// No description provided for @cookResultSaveLeftovers.
  ///
  /// In vi, this message translates to:
  /// **'Lưu phần ăn thừa'**
  String get cookResultSaveLeftovers;

  /// No description provided for @cookResultViewPantry.
  ///
  /// In vi, this message translates to:
  /// **'Xem kho'**
  String get cookResultViewPantry;

  /// No description provided for @cookResultWasteKgSuffix.
  ///
  /// In vi, this message translates to:
  /// **' · tránh bỏ phí ~{kg} kg thực phẩm'**
  String cookResultWasteKgSuffix(String kg);

  /// No description provided for @cookResultUsedNearExpiryPrefix.
  ///
  /// In vi, this message translates to:
  /// **'Bạn vừa tận dụng '**
  String get cookResultUsedNearExpiryPrefix;

  /// No description provided for @cookResultUsedNearExpiryCount.
  ///
  /// In vi, this message translates to:
  /// **'{count} nguyên liệu cận hạn'**
  String cookResultUsedNearExpiryCount(int count);

  /// No description provided for @cookResultChangesHeader.
  ///
  /// In vi, this message translates to:
  /// **'THAY ĐỔI TRONG KHO'**
  String get cookResultChangesHeader;

  /// No description provided for @cookResultLowStock.
  ///
  /// In vi, this message translates to:
  /// **'{names} sắp hết'**
  String cookResultLowStock(String names);

  /// No description provided for @commonNotChosen.
  ///
  /// In vi, this message translates to:
  /// **'Chưa chọn'**
  String get commonNotChosen;

  /// No description provided for @daysCount.
  ///
  /// In vi, this message translates to:
  /// **'{days} ngày'**
  String daysCount(int days);

  /// No description provided for @daysApprox.
  ///
  /// In vi, this message translates to:
  /// **'~{days} ngày'**
  String daysApprox(int days);

  /// No description provided for @tierAll.
  ///
  /// In vi, this message translates to:
  /// **'Tất cả'**
  String get tierAll;

  /// No description provided for @pantryTitle.
  ///
  /// In vi, this message translates to:
  /// **'Kho thực phẩm'**
  String get pantryTitle;

  /// No description provided for @pantrySortPrefix.
  ///
  /// In vi, this message translates to:
  /// **'Sắp xếp: {label}'**
  String pantrySortPrefix(String label);

  /// No description provided for @pantryAddIngredient.
  ///
  /// In vi, this message translates to:
  /// **'Thêm nguyên liệu'**
  String get pantryAddIngredient;

  /// No description provided for @pantrySearchHint.
  ///
  /// In vi, this message translates to:
  /// **'Tìm trong tủ bếp…'**
  String get pantrySearchHint;

  /// No description provided for @pantryNoResults.
  ///
  /// In vi, this message translates to:
  /// **'Không có kết quả'**
  String get pantryNoResults;

  /// No description provided for @pantryNoResultsBody.
  ///
  /// In vi, this message translates to:
  /// **'Thử đổi bộ lọc hoặc từ khóa khác.'**
  String get pantryNoResultsBody;

  /// No description provided for @pantryEmptyTitle.
  ///
  /// In vi, this message translates to:
  /// **'Tủ bếp đang trống'**
  String get pantryEmptyTitle;

  /// No description provided for @pantryEmptyBody.
  ///
  /// In vi, this message translates to:
  /// **'Thêm nguyên liệu đầu tiên để nhận gợi ý món.'**
  String get pantryEmptyBody;

  /// No description provided for @pantrySectionNear.
  ///
  /// In vi, this message translates to:
  /// **'Cần dùng sớm'**
  String get pantrySectionNear;

  /// No description provided for @pantrySectionAll.
  ///
  /// In vi, this message translates to:
  /// **'Tất cả'**
  String get pantrySectionAll;

  /// No description provided for @pantrySectionRest.
  ///
  /// In vi, this message translates to:
  /// **'Còn hạn'**
  String get pantrySectionRest;

  /// No description provided for @pantryConsumedAll.
  ///
  /// In vi, this message translates to:
  /// **'Đã dùng hết {name}'**
  String pantryConsumedAll(String name);

  /// No description provided for @pantryUpdateFailed.
  ///
  /// In vi, this message translates to:
  /// **'Không cập nhật được. Thử lại.'**
  String get pantryUpdateFailed;

  /// No description provided for @pantryDeleteTitle.
  ///
  /// In vi, this message translates to:
  /// **'Xóa nguyên liệu?'**
  String get pantryDeleteTitle;

  /// No description provided for @pantryDeleteBody.
  ///
  /// In vi, this message translates to:
  /// **'“{name}” sẽ bị xóa khỏi kho.'**
  String pantryDeleteBody(String name);

  /// No description provided for @pantryDeleted.
  ///
  /// In vi, this message translates to:
  /// **'Đã xóa {name}'**
  String pantryDeleted(String name);

  /// No description provided for @pantryDeleteFailed.
  ///
  /// In vi, this message translates to:
  /// **'Không xóa được. Thử lại.'**
  String get pantryDeleteFailed;

  /// No description provided for @pantryNotFoundTitle.
  ///
  /// In vi, this message translates to:
  /// **'Không tìm thấy nguyên liệu'**
  String get pantryNotFoundTitle;

  /// No description provided for @pantryNotFoundBody.
  ///
  /// In vi, this message translates to:
  /// **'Có thể nó đã được dùng hết hoặc đã xóa khỏi kho.'**
  String get pantryNotFoundBody;

  /// No description provided for @pantryDeleteMenu.
  ///
  /// In vi, this message translates to:
  /// **'Xóa khỏi kho'**
  String get pantryDeleteMenu;

  /// No description provided for @pantryStatQuantity.
  ///
  /// In vi, this message translates to:
  /// **'Số lượng'**
  String get pantryStatQuantity;

  /// No description provided for @pantryStatExpiry.
  ///
  /// In vi, this message translates to:
  /// **'Hạn dùng'**
  String get pantryStatExpiry;

  /// No description provided for @pantryStatPrice.
  ///
  /// In vi, this message translates to:
  /// **'Giá'**
  String get pantryStatPrice;

  /// No description provided for @pantryStatStorage.
  ///
  /// In vi, this message translates to:
  /// **'Bảo quản'**
  String get pantryStatStorage;

  /// No description provided for @pantryFindDishes.
  ///
  /// In vi, this message translates to:
  /// **'Tìm món nấu từ nguyên liệu này'**
  String get pantryFindDishes;

  /// No description provided for @pantryDetailLocation.
  ///
  /// In vi, this message translates to:
  /// **'Vị trí bảo quản'**
  String get pantryDetailLocation;

  /// No description provided for @pantryDetailAdded.
  ///
  /// In vi, this message translates to:
  /// **'Ngày thêm'**
  String get pantryDetailAdded;

  /// No description provided for @pantryDetailPacked.
  ///
  /// In vi, this message translates to:
  /// **'Ngày đóng gói / mua'**
  String get pantryDetailPacked;

  /// No description provided for @pantryDetailSource.
  ///
  /// In vi, this message translates to:
  /// **'Nguồn nhập'**
  String get pantryDetailSource;

  /// No description provided for @pantryDetailShelfRef.
  ///
  /// In vi, this message translates to:
  /// **'Bảo quản tham khảo'**
  String get pantryDetailShelfRef;

  /// No description provided for @pantryDetailCardTitle.
  ///
  /// In vi, this message translates to:
  /// **'Chi tiết'**
  String get pantryDetailCardTitle;

  /// No description provided for @pantryAdjust.
  ///
  /// In vi, this message translates to:
  /// **'Điều chỉnh'**
  String get pantryAdjust;

  /// No description provided for @pantryConsumeAll.
  ///
  /// In vi, this message translates to:
  /// **'Đã dùng hết'**
  String get pantryConsumeAll;

  /// No description provided for @pantryItemUpdated.
  ///
  /// In vi, this message translates to:
  /// **'Đã cập nhật {name}'**
  String pantryItemUpdated(String name);

  /// No description provided for @pantryItemAdded.
  ///
  /// In vi, this message translates to:
  /// **'Đã thêm {name} vào kho'**
  String pantryItemAdded(String name);

  /// No description provided for @pantrySaveFailed.
  ///
  /// In vi, this message translates to:
  /// **'Không lưu được. Kiểm tra lại thông tin.'**
  String get pantrySaveFailed;

  /// No description provided for @pantryEditTitle.
  ///
  /// In vi, this message translates to:
  /// **'Sửa nguyên liệu'**
  String get pantryEditTitle;

  /// No description provided for @pantryAddTitle.
  ///
  /// In vi, this message translates to:
  /// **'Thêm nguyên liệu'**
  String get pantryAddTitle;

  /// No description provided for @pantryFieldName.
  ///
  /// In vi, this message translates to:
  /// **'Tên nguyên liệu'**
  String get pantryFieldName;

  /// No description provided for @pantryFieldNameHint.
  ///
  /// In vi, this message translates to:
  /// **'VD: Cà chua bi'**
  String get pantryFieldNameHint;

  /// No description provided for @pantryFieldCategory.
  ///
  /// In vi, this message translates to:
  /// **'Nhóm thực phẩm'**
  String get pantryFieldCategory;

  /// No description provided for @pantryFieldCategoryHint.
  ///
  /// In vi, this message translates to:
  /// **'VD: Rau củ'**
  String get pantryFieldCategoryHint;

  /// No description provided for @pantryFieldStorage.
  ///
  /// In vi, this message translates to:
  /// **'Nơi bảo quản'**
  String get pantryFieldStorage;

  /// No description provided for @pantryFieldExpiry.
  ///
  /// In vi, this message translates to:
  /// **'Hạn sử dụng'**
  String get pantryFieldExpiry;

  /// No description provided for @pantryFieldPrice.
  ///
  /// In vi, this message translates to:
  /// **'Giá (tùy chọn)'**
  String get pantryFieldPrice;

  /// No description provided for @pantrySaveChanges.
  ///
  /// In vi, this message translates to:
  /// **'Lưu thay đổi'**
  String get pantrySaveChanges;

  /// No description provided for @pantryAddToPantry.
  ///
  /// In vi, this message translates to:
  /// **'Thêm vào kho'**
  String get pantryAddToPantry;

  /// No description provided for @adjustQtyTitle.
  ///
  /// In vi, this message translates to:
  /// **'Cập nhật số lượng — {name}'**
  String adjustQtyTitle(String name);

  /// No description provided for @adjustQtySubtitle.
  ///
  /// In vi, this message translates to:
  /// **'Hiện có: {qty} · {tier}'**
  String adjustQtySubtitle(String qty, String tier);

  /// No description provided for @adjustQtyPartial.
  ///
  /// In vi, this message translates to:
  /// **'Dùng một phần'**
  String get adjustQtyPartial;

  /// No description provided for @adjustQtyAll.
  ///
  /// In vi, this message translates to:
  /// **'Dùng hết'**
  String get adjustQtyAll;

  /// No description provided for @adjustQtyRemaining.
  ///
  /// In vi, this message translates to:
  /// **'Còn lại sau khi dùng'**
  String get adjustQtyRemaining;

  /// No description provided for @onbDietTitle.
  ///
  /// In vi, this message translates to:
  /// **'Bạn muốn ăn theo hướng nào?'**
  String get onbDietTitle;

  /// No description provided for @onbDietSubtitle.
  ///
  /// In vi, this message translates to:
  /// **'Dùng để xếp hạng gợi ý món. Có thể đổi bất cứ lúc nào trong Cài đặt.'**
  String get onbDietSubtitle;

  /// No description provided for @onbLater.
  ///
  /// In vi, this message translates to:
  /// **'Để sau'**
  String get onbLater;

  /// No description provided for @onbMethodScan.
  ///
  /// In vi, this message translates to:
  /// **'Quét'**
  String get onbMethodScan;

  /// No description provided for @onbMethodVoice.
  ///
  /// In vi, this message translates to:
  /// **'Nói'**
  String get onbMethodVoice;

  /// No description provided for @onbMethodManual.
  ///
  /// In vi, this message translates to:
  /// **'Nhập tay'**
  String get onbMethodManual;

  /// No description provided for @onbPantryTitle.
  ///
  /// In vi, this message translates to:
  /// **'Thêm nguyên liệu chỉ trong vài giây'**
  String get onbPantryTitle;

  /// No description provided for @onbPantryBody.
  ///
  /// In vi, this message translates to:
  /// **'Quét tem nhãn hoặc hóa đơn để lấy sẵn tên, khối lượng, hạn dùng. Bận tay thì đọc bằng giọng nói. Không có bao bì thì nhập tay thật nhanh.'**
  String get onbPantryBody;

  /// No description provided for @onbPantryCta.
  ///
  /// In vi, this message translates to:
  /// **'Thêm nguyên liệu đầu tiên'**
  String get onbPantryCta;

  /// No description provided for @suggestionsTitle.
  ///
  /// In vi, this message translates to:
  /// **'Gợi ý cho bạn'**
  String get suggestionsTitle;

  /// No description provided for @suggestionsQuickCook.
  ///
  /// In vi, this message translates to:
  /// **'≤ 30 phút'**
  String get suggestionsQuickCook;

  /// No description provided for @suggestionsEmptyTitle.
  ///
  /// In vi, this message translates to:
  /// **'Chưa đủ nguyên liệu để gợi ý'**
  String get suggestionsEmptyTitle;

  /// No description provided for @suggestionsEmptyBody.
  ///
  /// In vi, this message translates to:
  /// **'Thêm vài nguyên liệu vào kho để nhận 3–5 gợi ý món.'**
  String get suggestionsEmptyBody;

  /// No description provided for @suggestionsCaption.
  ///
  /// In vi, this message translates to:
  /// **'{count} món hợp nhất với tủ bếp hiện tại · ưu tiên đồ cận hạn'**
  String suggestionsCaption(int count);

  /// No description provided for @suggestionsWhyScore.
  ///
  /// In vi, this message translates to:
  /// **'Vì sao điểm này?'**
  String get suggestionsWhyScore;

  /// No description provided for @chipUseNearExpiry.
  ///
  /// In vi, this message translates to:
  /// **'Dùng {count} đồ cận hạn'**
  String chipUseNearExpiry(int count);

  /// No description provided for @chipAvailable.
  ///
  /// In vi, this message translates to:
  /// **'Có sẵn {percent}%'**
  String chipAvailable(int percent);

  /// No description provided for @chipToBuy.
  ///
  /// In vi, this message translates to:
  /// **'Cần mua {count}'**
  String chipToBuy(int count);

  /// No description provided for @chipNoBuy.
  ///
  /// In vi, this message translates to:
  /// **'Không cần mua'**
  String get chipNoBuy;

  /// No description provided for @scoreSheetTitle.
  ///
  /// In vi, this message translates to:
  /// **'Vì sao “{name}” đạt {score} điểm?'**
  String scoreSheetTitle(String name, int score);

  /// No description provided for @scoreFormula.
  ///
  /// In vi, this message translates to:
  /// **'Điểm = 0.4·E + 0.3·A + 0.2·P + 0.1·U'**
  String get scoreFormula;

  /// No description provided for @scoreCompE.
  ///
  /// In vi, this message translates to:
  /// **'Dùng đồ cận hạn'**
  String get scoreCompE;

  /// No description provided for @scoreCompA.
  ///
  /// In vi, this message translates to:
  /// **'Tỉ lệ nguyên liệu có sẵn'**
  String get scoreCompA;

  /// No description provided for @scoreCompP.
  ///
  /// In vi, this message translates to:
  /// **'Hợp khẩu phần & sở thích'**
  String get scoreCompP;

  /// No description provided for @scoreCompU.
  ///
  /// In vi, this message translates to:
  /// **'Ít phải mua thêm'**
  String get scoreCompU;

  /// No description provided for @scoreReasonENone.
  ///
  /// In vi, this message translates to:
  /// **'Không dùng nguyên liệu cận hạn nào'**
  String get scoreReasonENone;

  /// No description provided for @scoreReasonE.
  ///
  /// In vi, this message translates to:
  /// **'Dùng {count} nguyên liệu cận hạn: {list}'**
  String scoreReasonE(int count, String list);

  /// No description provided for @scoreReasonA.
  ///
  /// In vi, this message translates to:
  /// **'{percent}% nguyên liệu đã có trong tủ bếp'**
  String scoreReasonA(int percent);

  /// No description provided for @scoreReasonP.
  ///
  /// In vi, this message translates to:
  /// **'{servings} khẩu phần · {kcal} kcal · {minutes} phút'**
  String scoreReasonP(int servings, int kcal, int minutes);

  /// No description provided for @scoreReasonUNone.
  ///
  /// In vi, this message translates to:
  /// **'Không phải mua thêm nguyên liệu nào'**
  String get scoreReasonUNone;

  /// No description provided for @scoreReasonU.
  ///
  /// In vi, this message translates to:
  /// **'Chỉ cần mua thêm {count} nguyên liệu'**
  String scoreReasonU(int count);

  /// No description provided for @dishDetailTitle.
  ///
  /// In vi, this message translates to:
  /// **'Chi tiết món'**
  String get dishDetailTitle;

  /// No description provided for @dishIngredientsWithServings.
  ///
  /// In vi, this message translates to:
  /// **'Nguyên liệu · {servings} phần'**
  String dishIngredientsWithServings(int servings);

  /// No description provided for @dishSeasonings.
  ///
  /// In vi, this message translates to:
  /// **'Gia vị'**
  String get dishSeasonings;

  /// No description provided for @dishHowTo.
  ///
  /// In vi, this message translates to:
  /// **'Cách làm'**
  String get dishHowTo;

  /// No description provided for @dishServingsLabel.
  ///
  /// In vi, this message translates to:
  /// **'Khẩu phần'**
  String get dishServingsLabel;

  /// No description provided for @dishCookedThis.
  ///
  /// In vi, this message translates to:
  /// **'Đã nấu món này'**
  String get dishCookedThis;

  /// No description provided for @dishAddedToShopping.
  ///
  /// In vi, this message translates to:
  /// **'Đã thêm {count} nguyên liệu vào danh sách mua'**
  String dishAddedToShopping(int count);

  /// No description provided for @dishShoppingNotReady.
  ///
  /// In vi, this message translates to:
  /// **'Danh sách mua chưa sẵn sàng — thử lại sau.'**
  String get dishShoppingNotReady;

  /// No description provided for @dishAddMissing.
  ///
  /// In vi, this message translates to:
  /// **'Thêm {count} nguyên liệu thiếu vào danh sách mua'**
  String dishAddMissing(int count);

  /// No description provided for @checklistNearExpiry.
  ///
  /// In vi, this message translates to:
  /// **'cận hạn'**
  String get checklistNearExpiry;

  /// No description provided for @checklistToBuy.
  ///
  /// In vi, this message translates to:
  /// **'cần mua'**
  String get checklistToBuy;

  /// No description provided for @macroEstimateNote.
  ///
  /// In vi, this message translates to:
  /// **'Ước tính theo 1 khẩu phần · nguồn Viện Dinh dưỡng Quốc gia'**
  String get macroEstimateNote;

  /// No description provided for @ingredientCount.
  ///
  /// In vi, this message translates to:
  /// **'{count} nguyên liệu'**
  String ingredientCount(int count);

  /// No description provided for @seeAll.
  ///
  /// In vi, this message translates to:
  /// **'Xem tất cả'**
  String get seeAll;

  /// No description provided for @greetingMorning.
  ///
  /// In vi, this message translates to:
  /// **'Chào buổi sáng'**
  String get greetingMorning;

  /// No description provided for @greetingNoon.
  ///
  /// In vi, this message translates to:
  /// **'Chào buổi trưa'**
  String get greetingNoon;

  /// No description provided for @greetingAfternoon.
  ///
  /// In vi, this message translates to:
  /// **'Chào buổi chiều'**
  String get greetingAfternoon;

  /// No description provided for @greetingEvening.
  ///
  /// In vi, this message translates to:
  /// **'Chào buổi tối'**
  String get greetingEvening;

  /// No description provided for @homeWhatToEat.
  ///
  /// In vi, this message translates to:
  /// **'Hôm nay ăn gì?'**
  String get homeWhatToEat;

  /// No description provided for @homeEmptyTitle.
  ///
  /// In vi, this message translates to:
  /// **'Kho của bạn đang trống'**
  String get homeEmptyTitle;

  /// No description provided for @homeEmptyBody.
  ///
  /// In vi, this message translates to:
  /// **'Thêm vài nguyên liệu để nhận gợi ý món và nhắc hạn sử dụng.'**
  String get homeEmptyBody;

  /// No description provided for @homeAddFirst.
  ///
  /// In vi, this message translates to:
  /// **'Thêm nguyên liệu đầu tiên'**
  String get homeAddFirst;

  /// No description provided for @homeTileSuggestDish.
  ///
  /// In vi, this message translates to:
  /// **'Gợi ý món'**
  String get homeTileSuggestDish;

  /// No description provided for @homeSuggestionCount.
  ///
  /// In vi, this message translates to:
  /// **'{count} món phù hợp'**
  String homeSuggestionCount(int count);

  /// No description provided for @homeSuggestFallback.
  ///
  /// In vi, this message translates to:
  /// **'Món hợp tủ bếp'**
  String get homeSuggestFallback;

  /// No description provided for @homeQuickAdd.
  ///
  /// In vi, this message translates to:
  /// **'Thêm nhanh'**
  String get homeQuickAdd;

  /// No description provided for @homeQuickAddSub.
  ///
  /// In vi, this message translates to:
  /// **'Tem · Hóa đơn · Giọng nói'**
  String get homeQuickAddSub;

  /// No description provided for @homeUseSoon.
  ///
  /// In vi, this message translates to:
  /// **'Cần dùng sớm'**
  String get homeUseSoon;

  /// No description provided for @homeNoNearExpiry.
  ///
  /// In vi, this message translates to:
  /// **'Không có nguyên liệu nào cận hạn. Tủ bếp của bạn rất tươi tốt!'**
  String get homeNoNearExpiry;

  /// No description provided for @homeSuggestionsLoadFail.
  ///
  /// In vi, this message translates to:
  /// **'Chưa tải được gợi ý. Kéo xuống để làm mới.'**
  String get homeSuggestionsLoadFail;

  /// No description provided for @wdMon.
  ///
  /// In vi, this message translates to:
  /// **'T2'**
  String get wdMon;

  /// No description provided for @wdTue.
  ///
  /// In vi, this message translates to:
  /// **'T3'**
  String get wdTue;

  /// No description provided for @wdWed.
  ///
  /// In vi, this message translates to:
  /// **'T4'**
  String get wdWed;

  /// No description provided for @wdThu.
  ///
  /// In vi, this message translates to:
  /// **'T5'**
  String get wdThu;

  /// No description provided for @wdFri.
  ///
  /// In vi, this message translates to:
  /// **'T6'**
  String get wdFri;

  /// No description provided for @wdSat.
  ///
  /// In vi, this message translates to:
  /// **'T7'**
  String get wdSat;

  /// No description provided for @wdSun.
  ///
  /// In vi, this message translates to:
  /// **'CN'**
  String get wdSun;

  /// No description provided for @mealPlanTitle.
  ///
  /// In vi, this message translates to:
  /// **'Thực đơn tuần'**
  String get mealPlanTitle;

  /// No description provided for @mealPlanGenerateShopping.
  ///
  /// In vi, this message translates to:
  /// **'Tạo danh sách mua sắm'**
  String get mealPlanGenerateShopping;

  /// No description provided for @mealPlanPickDish.
  ///
  /// In vi, this message translates to:
  /// **'Chọn món'**
  String get mealPlanPickDish;

  /// No description provided for @mealPlanPickDishSub.
  ///
  /// In vi, this message translates to:
  /// **'Từ gợi ý hợp tủ bếp của bạn'**
  String get mealPlanPickDishSub;

  /// No description provided for @mealSlotChosen.
  ///
  /// In vi, this message translates to:
  /// **'Món đã chọn'**
  String get mealSlotChosen;

  /// No description provided for @mealSlotAdd.
  ///
  /// In vi, this message translates to:
  /// **'+ Thêm'**
  String get mealSlotAdd;

  /// No description provided for @reportsTitle.
  ///
  /// In vi, this message translates to:
  /// **'Chống lãng phí'**
  String get reportsTitle;

  /// No description provided for @reportsEmptyTitle.
  ///
  /// In vi, this message translates to:
  /// **'Chưa có dữ liệu'**
  String get reportsEmptyTitle;

  /// No description provided for @reportsEmptyBody.
  ///
  /// In vi, this message translates to:
  /// **'Nấu vài món dùng nguyên liệu cận hạn để xem bạn tiết kiệm được bao nhiêu.'**
  String get reportsEmptyBody;

  /// No description provided for @reportsWeeklyCard.
  ///
  /// In vi, this message translates to:
  /// **'Nguyên liệu cứu được theo tuần'**
  String get reportsWeeklyCard;

  /// No description provided for @reportsByCategoryCard.
  ///
  /// In vi, this message translates to:
  /// **'Theo nhóm thực phẩm'**
  String get reportsByCategoryCard;

  /// No description provided for @reportsHeroPeriod.
  ///
  /// In vi, this message translates to:
  /// **'{period} · nguyên liệu dùng trước hạn'**
  String reportsHeroPeriod(String period);

  /// No description provided for @reportsHeroDetail.
  ///
  /// In vi, this message translates to:
  /// **'≈ {kg} thực phẩm tránh bị bỏ phí · {dishes} món đã nấu'**
  String reportsHeroDetail(String kg, int dishes);

  /// No description provided for @prefsTitle.
  ///
  /// In vi, this message translates to:
  /// **'Tùy chọn'**
  String get prefsTitle;

  /// No description provided for @prefsGroupMeal.
  ///
  /// In vi, this message translates to:
  /// **'Bữa ăn'**
  String get prefsGroupMeal;

  /// No description provided for @prefsDietary.
  ///
  /// In vi, this message translates to:
  /// **'Ưu tiên dinh dưỡng'**
  String get prefsDietary;

  /// No description provided for @prefsUnit.
  ///
  /// In vi, this message translates to:
  /// **'Đơn vị đo mặc định'**
  String get prefsUnit;

  /// No description provided for @prefsCurrency.
  ///
  /// In vi, this message translates to:
  /// **'Tiền tệ hiển thị'**
  String get prefsCurrency;

  /// No description provided for @prefsCurrencyValue.
  ///
  /// In vi, this message translates to:
  /// **'VND (đ)'**
  String get prefsCurrencyValue;

  /// No description provided for @prefsGroupAppearance.
  ///
  /// In vi, this message translates to:
  /// **'Giao diện'**
  String get prefsGroupAppearance;

  /// No description provided for @prefsLanguage.
  ///
  /// In vi, this message translates to:
  /// **'Ngôn ngữ'**
  String get prefsLanguage;

  /// No description provided for @langVi.
  ///
  /// In vi, this message translates to:
  /// **'Tiếng Việt'**
  String get langVi;

  /// No description provided for @langEn.
  ///
  /// In vi, this message translates to:
  /// **'English'**
  String get langEn;

  /// No description provided for @prefsTheme.
  ///
  /// In vi, this message translates to:
  /// **'Chủ đề'**
  String get prefsTheme;

  /// No description provided for @themeLight.
  ///
  /// In vi, this message translates to:
  /// **'Sáng'**
  String get themeLight;

  /// No description provided for @themeDark.
  ///
  /// In vi, this message translates to:
  /// **'Tối'**
  String get themeDark;

  /// No description provided for @themeSystem.
  ///
  /// In vi, this message translates to:
  /// **'Theo hệ thống'**
  String get themeSystem;

  /// No description provided for @catVegetables.
  ///
  /// In vi, this message translates to:
  /// **'Rau củ'**
  String get catVegetables;

  /// No description provided for @catMeatSeafood.
  ///
  /// In vi, this message translates to:
  /// **'Thịt & Hải sản'**
  String get catMeatSeafood;

  /// No description provided for @catSpices.
  ///
  /// In vi, this message translates to:
  /// **'Gia vị'**
  String get catSpices;

  /// No description provided for @catDairyEgg.
  ///
  /// In vi, this message translates to:
  /// **'Trứng & Sữa'**
  String get catDairyEgg;

  /// No description provided for @catDryGoods.
  ///
  /// In vi, this message translates to:
  /// **'Đồ khô'**
  String get catDryGoods;

  /// No description provided for @catOther.
  ///
  /// In vi, this message translates to:
  /// **'Khác'**
  String get catOther;

  /// No description provided for @scanSaveError.
  ///
  /// In vi, this message translates to:
  /// **'Lỗi lưu nguyên liệu: {error}'**
  String scanSaveError(String error);

  /// No description provided for @scanAddedToPantry.
  ///
  /// In vi, this message translates to:
  /// **'Đã thêm {name} vào kho!'**
  String scanAddedToPantry(String name);

  /// No description provided for @scanAddedCountToPantry.
  ///
  /// In vi, this message translates to:
  /// **'Đã thêm {count} nguyên liệu vào kho!'**
  String scanAddedCountToPantry(int count);

  /// No description provided for @scanNoName.
  ///
  /// In vi, this message translates to:
  /// **'Chưa rõ tên'**
  String get scanNoName;

  /// No description provided for @scanNeedsCheckShort.
  ///
  /// In vi, this message translates to:
  /// **'Kiểm tra'**
  String get scanNeedsCheckShort;

  /// No description provided for @scanAddRow.
  ///
  /// In vi, this message translates to:
  /// **'Thêm dòng'**
  String get scanAddRow;

  /// No description provided for @chooserScanLabel.
  ///
  /// In vi, this message translates to:
  /// **'Quét tem nhãn'**
  String get chooserScanLabel;

  /// No description provided for @chooserScanLabelSub.
  ///
  /// In vi, this message translates to:
  /// **'Chụp nhãn cân trên sản phẩm đóng gói'**
  String get chooserScanLabelSub;

  /// No description provided for @chooserScanReceipt.
  ///
  /// In vi, this message translates to:
  /// **'Quét hóa đơn'**
  String get chooserScanReceipt;

  /// No description provided for @chooserScanReceiptSub.
  ///
  /// In vi, this message translates to:
  /// **'Chụp hóa đơn, thêm nhiều mục một lúc'**
  String get chooserScanReceiptSub;

  /// No description provided for @chooserVoice.
  ///
  /// In vi, this message translates to:
  /// **'Nói'**
  String get chooserVoice;

  /// No description provided for @chooserVoiceSub.
  ///
  /// In vi, this message translates to:
  /// **'Đọc tên nguyên liệu và số lượng'**
  String get chooserVoiceSub;

  /// No description provided for @chooserManual.
  ///
  /// In vi, this message translates to:
  /// **'Nhập tay'**
  String get chooserManual;

  /// No description provided for @chooserManualSub.
  ///
  /// In vi, this message translates to:
  /// **'Tự chọn từ danh mục nguyên liệu'**
  String get chooserManualSub;

  /// No description provided for @camModeLabel.
  ///
  /// In vi, this message translates to:
  /// **'Tem nhãn'**
  String get camModeLabel;

  /// No description provided for @camModeReceipt.
  ///
  /// In vi, this message translates to:
  /// **'Hóa đơn'**
  String get camModeReceipt;

  /// No description provided for @camScanTitle.
  ///
  /// In vi, this message translates to:
  /// **'Quét {kind}'**
  String camScanTitle(String kind);

  /// No description provided for @camNoCamera.
  ///
  /// In vi, this message translates to:
  /// **'Thiết bị không có máy ảnh.'**
  String get camNoCamera;

  /// No description provided for @camOpenError.
  ///
  /// In vi, this message translates to:
  /// **'Không mở được máy ảnh: {error}'**
  String camOpenError(String error);

  /// No description provided for @camNoFlash.
  ///
  /// In vi, this message translates to:
  /// **'Đèn flash không khả dụng trên thiết bị này.'**
  String get camNoFlash;

  /// No description provided for @camShootError.
  ///
  /// In vi, this message translates to:
  /// **'Không chụp được: {error}'**
  String camShootError(String error);

  /// No description provided for @camGalleryError.
  ///
  /// In vi, this message translates to:
  /// **'Không mở được thư viện ảnh: {error}'**
  String camGalleryError(String error);

  /// No description provided for @camReading.
  ///
  /// In vi, this message translates to:
  /// **'Đang đọc thông tin…'**
  String get camReading;

  /// No description provided for @camOpening.
  ///
  /// In vi, this message translates to:
  /// **'Đang mở máy ảnh…'**
  String get camOpening;

  /// No description provided for @camGuideLabel.
  ///
  /// In vi, this message translates to:
  /// **'Đưa nhãn cân vào khung, giữ máy thẳng'**
  String get camGuideLabel;

  /// No description provided for @camGuideReceipt.
  ///
  /// In vi, this message translates to:
  /// **'Đưa toàn bộ hóa đơn vào khung'**
  String get camGuideReceipt;

  /// No description provided for @camPermissionNeeded.
  ///
  /// In vi, this message translates to:
  /// **'Cần quyền máy ảnh để quét trực tiếp.'**
  String get camPermissionNeeded;

  /// No description provided for @camGrantPermission.
  ///
  /// In vi, this message translates to:
  /// **'Cấp quyền máy ảnh'**
  String get camGrantPermission;

  /// No description provided for @camUseGallery.
  ///
  /// In vi, this message translates to:
  /// **'Dùng ảnh có sẵn'**
  String get camUseGallery;

  /// No description provided for @reviewLabelTitle.
  ///
  /// In vi, this message translates to:
  /// **'Kiểm tra thông tin'**
  String get reviewLabelTitle;

  /// No description provided for @reviewFieldsRead.
  ///
  /// In vi, this message translates to:
  /// **'Đã đọc được {count} trường. Kiểm tra lại trường được đánh dấu trước khi lưu.'**
  String reviewFieldsRead(int count);

  /// No description provided for @reviewNetWeight.
  ///
  /// In vi, this message translates to:
  /// **'Khối lượng tịnh'**
  String get reviewNetWeight;

  /// No description provided for @reviewPackedDate.
  ///
  /// In vi, this message translates to:
  /// **'Ngày đóng gói'**
  String get reviewPackedDate;

  /// No description provided for @reviewStorageTier.
  ///
  /// In vi, this message translates to:
  /// **'Tầng bảo quản'**
  String get reviewStorageTier;

  /// No description provided for @reviewCategory.
  ///
  /// In vi, this message translates to:
  /// **'Danh mục'**
  String get reviewCategory;

  /// No description provided for @reviewNameHint.
  ///
  /// In vi, this message translates to:
  /// **'Nhập tên nguyên liệu'**
  String get reviewNameHint;

  /// No description provided for @reviewUnit.
  ///
  /// In vi, this message translates to:
  /// **'Đơn vị'**
  String get reviewUnit;

  /// No description provided for @reviewPurchasePrice.
  ///
  /// In vi, this message translates to:
  /// **'Giá mua (VNĐ)'**
  String get reviewPurchasePrice;

  /// No description provided for @reviewPriceHint.
  ///
  /// In vi, this message translates to:
  /// **'Ví dụ: 18000'**
  String get reviewPriceHint;

  /// No description provided for @reviewPickCategory.
  ///
  /// In vi, this message translates to:
  /// **'Chọn danh mục'**
  String get reviewPickCategory;

  /// No description provided for @reviewLabelPhoto.
  ///
  /// In vi, this message translates to:
  /// **'Ảnh tem nhãn'**
  String get reviewLabelPhoto;

  /// No description provided for @reviewRetake.
  ///
  /// In vi, this message translates to:
  /// **'Chụp lại'**
  String get reviewRetake;

  /// No description provided for @reviewReceiptTitle.
  ///
  /// In vi, this message translates to:
  /// **'Hóa đơn — {count} mục'**
  String reviewReceiptTitle(int count);

  /// No description provided for @reviewSelectedOf.
  ///
  /// In vi, this message translates to:
  /// **' / {count} mục được chọn'**
  String reviewSelectedOf(int count);

  /// No description provided for @reviewDeselectAll.
  ///
  /// In vi, this message translates to:
  /// **'Bỏ chọn tất cả'**
  String get reviewDeselectAll;

  /// No description provided for @reviewSelectAll.
  ///
  /// In vi, this message translates to:
  /// **'Chọn tất cả'**
  String get reviewSelectAll;

  /// No description provided for @reviewAddCount.
  ///
  /// In vi, this message translates to:
  /// **'Thêm {count} mục vào kho'**
  String reviewAddCount(int count);

  /// No description provided for @reviewPickAtLeastOne.
  ///
  /// In vi, this message translates to:
  /// **'Chọn ít nhất 1 mục'**
  String get reviewPickAtLeastOne;

  /// No description provided for @reviewEditItem.
  ///
  /// In vi, this message translates to:
  /// **'Chỉnh sửa nguyên liệu'**
  String get reviewEditItem;

  /// No description provided for @reviewRemoveItem.
  ///
  /// In vi, this message translates to:
  /// **'Xóa mục này'**
  String get reviewRemoveItem;

  /// No description provided for @voiceCaptureTitle.
  ///
  /// In vi, this message translates to:
  /// **'Nói để thêm'**
  String get voiceCaptureTitle;

  /// No description provided for @voiceCapturePrompt.
  ///
  /// In vi, this message translates to:
  /// **'Đọc tên nguyên liệu và số lượng'**
  String get voiceCapturePrompt;

  /// No description provided for @voiceCaptureExample.
  ///
  /// In vi, this message translates to:
  /// **'VD: “2 lạng thịt bò, 1 bó cải bó xôi, 3 quả trứng”'**
  String get voiceCaptureExample;

  /// No description provided for @voiceListening.
  ///
  /// In vi, this message translates to:
  /// **'Đang nghe…'**
  String get voiceListening;

  /// No description provided for @voiceMicOff.
  ///
  /// In vi, this message translates to:
  /// **'Chưa bật được micro — cứ đọc rồi kiểm tra'**
  String get voiceMicOff;

  /// No description provided for @voiceStopReview.
  ///
  /// In vi, this message translates to:
  /// **'Dừng & Kiểm tra'**
  String get voiceStopReview;

  /// No description provided for @voiceReviewTitle.
  ///
  /// In vi, this message translates to:
  /// **'Kiểm tra kết quả'**
  String get voiceReviewTitle;

  /// No description provided for @voiceRerecord.
  ///
  /// In vi, this message translates to:
  /// **'Ghi lại'**
  String get voiceRerecord;

  /// No description provided for @voiceParsedCount.
  ///
  /// In vi, this message translates to:
  /// **'Đã bóc tách {count} nguyên liệu'**
  String voiceParsedCount(int count);

  /// No description provided for @voiceAddCount.
  ///
  /// In vi, this message translates to:
  /// **'Thêm {count} nguyên liệu'**
  String voiceAddCount(int count);

  /// No description provided for @scanFailLabelTitle.
  ///
  /// In vi, this message translates to:
  /// **'Không đọc được nhãn'**
  String get scanFailLabelTitle;

  /// No description provided for @scanFailReceiptTitle.
  ///
  /// In vi, this message translates to:
  /// **'Không đọc được hóa đơn'**
  String get scanFailReceiptTitle;

  /// No description provided for @scanFailVoiceTitle.
  ///
  /// In vi, this message translates to:
  /// **'Không nghe rõ'**
  String get scanFailVoiceTitle;

  /// No description provided for @scanFailVoiceReason1.
  ///
  /// In vi, this message translates to:
  /// **'Môi trường quá ồn'**
  String get scanFailVoiceReason1;

  /// No description provided for @scanFailVoiceReason2.
  ///
  /// In vi, this message translates to:
  /// **'Nói quá nhanh hoặc quá nhỏ'**
  String get scanFailVoiceReason2;

  /// No description provided for @scanFailVoiceReason3.
  ///
  /// In vi, this message translates to:
  /// **'Micro bị che'**
  String get scanFailVoiceReason3;

  /// No description provided for @scanFailImgReason1.
  ///
  /// In vi, this message translates to:
  /// **'Ảnh bị mờ hoặc chụp nghiêng'**
  String get scanFailImgReason1;

  /// No description provided for @scanFailImgReason2.
  ///
  /// In vi, this message translates to:
  /// **'Nhãn bị rách hoặc phai mực'**
  String get scanFailImgReason2;

  /// No description provided for @scanFailImgReason3.
  ///
  /// In vi, this message translates to:
  /// **'Thiếu sáng khi chụp'**
  String get scanFailImgReason3;

  /// No description provided for @scanFailRerecord.
  ///
  /// In vi, this message translates to:
  /// **'Thu lại'**
  String get scanFailRerecord;

  /// No description provided for @featureComingInMilestone.
  ///
  /// In vi, this message translates to:
  /// **'Sẽ hiện thực ở {milestone}'**
  String featureComingInMilestone(String milestone);

  /// No description provided for @authSignIn.
  ///
  /// In vi, this message translates to:
  /// **'Đăng nhập'**
  String get authSignIn;

  /// No description provided for @authSignUp.
  ///
  /// In vi, this message translates to:
  /// **'Đăng ký'**
  String get authSignUp;

  /// No description provided for @authCreateAccount.
  ///
  /// In vi, this message translates to:
  /// **'Tạo tài khoản'**
  String get authCreateAccount;

  /// No description provided for @authEmail.
  ///
  /// In vi, this message translates to:
  /// **'Email'**
  String get authEmail;

  /// No description provided for @authPassword.
  ///
  /// In vi, this message translates to:
  /// **'Mật khẩu'**
  String get authPassword;

  /// No description provided for @authFullName.
  ///
  /// In vi, this message translates to:
  /// **'Họ và tên'**
  String get authFullName;

  /// No description provided for @authFullNameHint.
  ///
  /// In vi, this message translates to:
  /// **'Nguyễn Văn A'**
  String get authFullNameHint;

  /// No description provided for @authPasswordHint.
  ///
  /// In vi, this message translates to:
  /// **'Ít nhất 8 ký tự'**
  String get authPasswordHint;

  /// No description provided for @authForgotQ.
  ///
  /// In vi, this message translates to:
  /// **'Quên mật khẩu?'**
  String get authForgotQ;

  /// No description provided for @authForgotTitle.
  ///
  /// In vi, this message translates to:
  /// **'Quên mật khẩu'**
  String get authForgotTitle;

  /// No description provided for @authInvalidEmail.
  ///
  /// In vi, this message translates to:
  /// **'Email không hợp lệ'**
  String get authInvalidEmail;

  /// No description provided for @authEnterPassword.
  ///
  /// In vi, this message translates to:
  /// **'Nhập mật khẩu'**
  String get authEnterPassword;

  /// No description provided for @authEnterName.
  ///
  /// In vi, this message translates to:
  /// **'Nhập họ và tên'**
  String get authEnterName;

  /// No description provided for @authPasswordTooShort.
  ///
  /// In vi, this message translates to:
  /// **'Ít nhất 8 ký tự'**
  String get authPasswordTooShort;

  /// No description provided for @authPhone.
  ///
  /// In vi, this message translates to:
  /// **'Số điện thoại'**
  String get authPhone;

  /// No description provided for @authInvalidPhone.
  ///
  /// In vi, this message translates to:
  /// **'Số điện thoại không hợp lệ'**
  String get authInvalidPhone;

  /// No description provided for @authOtpTitle.
  ///
  /// In vi, this message translates to:
  /// **'Nhập mã xác thực'**
  String get authOtpTitle;

  /// No description provided for @authOtpSubtitle.
  ///
  /// In vi, this message translates to:
  /// **'Mã gồm 6 chữ số đã được gửi tới {phone}.'**
  String authOtpSubtitle(String phone);

  /// No description provided for @authOtpLabel.
  ///
  /// In vi, this message translates to:
  /// **'Mã xác thực'**
  String get authOtpLabel;

  /// No description provided for @authOtpInvalid.
  ///
  /// In vi, this message translates to:
  /// **'Mã gồm 6 chữ số'**
  String get authOtpInvalid;

  /// No description provided for @authOtpConfirm.
  ///
  /// In vi, this message translates to:
  /// **'Xác nhận'**
  String get authOtpConfirm;

  /// No description provided for @authOtpResendCta.
  ///
  /// In vi, this message translates to:
  /// **'Gửi lại mã'**
  String get authOtpResendCta;

  /// No description provided for @authOtpResent.
  ///
  /// In vi, this message translates to:
  /// **'Đã gửi lại mã.'**
  String get authOtpResent;

  /// No description provided for @authOtpMissingArgs.
  ///
  /// In vi, this message translates to:
  /// **'Thiếu thông tin. Quay lại và thử lại.'**
  String get authOtpMissingArgs;

  /// No description provided for @welcomeSlide1Title.
  ///
  /// In vi, this message translates to:
  /// **'Biến nguyên liệu đang có thành bữa ăn'**
  String get welcomeSlide1Title;

  /// No description provided for @welcomeSlide1Body.
  ///
  /// In vi, this message translates to:
  /// **'SweepFood theo dõi hạn dùng và luôn đẩy những món cần dùng sớm lên đầu.'**
  String get welcomeSlide1Body;

  /// No description provided for @welcomeSlide2Title.
  ///
  /// In vi, this message translates to:
  /// **'Gợi ý món hợp tủ bếp của bạn'**
  String get welcomeSlide2Title;

  /// No description provided for @welcomeSlide2Body.
  ///
  /// In vi, this message translates to:
  /// **'3–5 món mỗi lần, chấm điểm theo nguyên liệu sẵn có và đồ sắp hết hạn.'**
  String get welcomeSlide2Body;

  /// No description provided for @welcomeSlide3Title.
  ///
  /// In vi, this message translates to:
  /// **'Nấu hết đồ, bớt lãng phí'**
  String get welcomeSlide3Title;

  /// No description provided for @welcomeSlide3Body.
  ///
  /// In vi, this message translates to:
  /// **'Xem bạn đã dùng kịp bao nhiêu nguyên liệu trước hạn — tính bằng kg tránh bỏ phí.'**
  String get welcomeSlide3Body;

  /// No description provided for @welcomeStart.
  ///
  /// In vi, this message translates to:
  /// **'Bắt đầu'**
  String get welcomeStart;

  /// No description provided for @welcomeHaveAccount.
  ///
  /// In vi, this message translates to:
  /// **'Đã có tài khoản? Đăng nhập'**
  String get welcomeHaveAccount;

  /// No description provided for @loginSubtitle.
  ///
  /// In vi, this message translates to:
  /// **'Tiếp tục quản lý tủ bếp của bạn'**
  String get loginSubtitle;

  /// No description provided for @loginNoAccount.
  ///
  /// In vi, this message translates to:
  /// **'Chưa có tài khoản? '**
  String get loginNoAccount;

  /// No description provided for @loginFailed.
  ///
  /// In vi, this message translates to:
  /// **'Đăng nhập không thành công. Thử lại nhé.'**
  String get loginFailed;

  /// No description provided for @registerSubtitle.
  ///
  /// In vi, this message translates to:
  /// **'Bắt đầu tiết kiệm thực phẩm cùng SweepFood'**
  String get registerSubtitle;

  /// No description provided for @registerHaveAccount.
  ///
  /// In vi, this message translates to:
  /// **'Đã có tài khoản? '**
  String get registerHaveAccount;

  /// No description provided for @registerNeedTerms.
  ///
  /// In vi, this message translates to:
  /// **'Cần đồng ý với Điều khoản để tiếp tục.'**
  String get registerNeedTerms;

  /// No description provided for @termsPrefix.
  ///
  /// In vi, this message translates to:
  /// **'Tôi đồng ý với '**
  String get termsPrefix;

  /// No description provided for @termsOfUse.
  ///
  /// In vi, this message translates to:
  /// **'Điều khoản sử dụng'**
  String get termsOfUse;

  /// No description provided for @termsAnd.
  ///
  /// In vi, this message translates to:
  /// **' và '**
  String get termsAnd;

  /// No description provided for @termsPrivacy.
  ///
  /// In vi, this message translates to:
  /// **'Chính sách bảo mật'**
  String get termsPrivacy;

  /// No description provided for @forgotSubtitle.
  ///
  /// In vi, this message translates to:
  /// **'Nhập số điện thoại tài khoản, chúng tôi sẽ gửi mã đặt lại mật khẩu.'**
  String get forgotSubtitle;

  /// No description provided for @forgotSendLink.
  ///
  /// In vi, this message translates to:
  /// **'Gửi liên kết'**
  String get forgotSendLink;

  /// No description provided for @forgotSendCode.
  ///
  /// In vi, this message translates to:
  /// **'Gửi mã'**
  String get forgotSendCode;

  /// No description provided for @forgotBackToLogin.
  ///
  /// In vi, this message translates to:
  /// **'Quay lại đăng nhập'**
  String get forgotBackToLogin;

  /// No description provided for @resetPasswordTitle.
  ///
  /// In vi, this message translates to:
  /// **'Đặt lại mật khẩu'**
  String get resetPasswordTitle;

  /// No description provided for @resetPasswordSubtitle.
  ///
  /// In vi, this message translates to:
  /// **'Nhập mã đã gửi tới {phone} và mật khẩu mới.'**
  String resetPasswordSubtitle(String phone);

  /// No description provided for @resetPasswordNewLabel.
  ///
  /// In vi, this message translates to:
  /// **'Mật khẩu mới'**
  String get resetPasswordNewLabel;

  /// No description provided for @resetPasswordCta.
  ///
  /// In vi, this message translates to:
  /// **'Đặt lại mật khẩu'**
  String get resetPasswordCta;

  /// No description provided for @resetPasswordDone.
  ///
  /// In vi, this message translates to:
  /// **'Đã đặt lại mật khẩu. Đăng nhập lại nhé.'**
  String get resetPasswordDone;

  /// No description provided for @forgotSentTo.
  ///
  /// In vi, this message translates to:
  /// **'Đã gửi tới {email}'**
  String forgotSentTo(String email);

  /// No description provided for @forgotCheckInbox.
  ///
  /// In vi, this message translates to:
  /// **'Kiểm tra hộp thư (kể cả mục spam). Liên kết hiệu lực trong 30 phút.'**
  String get forgotCheckInbox;

  /// No description provided for @commonYou.
  ///
  /// In vi, this message translates to:
  /// **'Bạn'**
  String get commonYou;

  /// No description provided for @dayToday.
  ///
  /// In vi, this message translates to:
  /// **'Hôm nay'**
  String get dayToday;

  /// No description provided for @dayYesterday.
  ///
  /// In vi, this message translates to:
  /// **'Hôm qua'**
  String get dayYesterday;

  /// No description provided for @willOpenInBrowser.
  ///
  /// In vi, this message translates to:
  /// **'Sẽ mở trong trình duyệt.'**
  String get willOpenInBrowser;

  /// No description provided for @notifTitle.
  ///
  /// In vi, this message translates to:
  /// **'Thông báo'**
  String get notifTitle;

  /// No description provided for @notifMarkAllRead.
  ///
  /// In vi, this message translates to:
  /// **'Đánh dấu đã đọc'**
  String get notifMarkAllRead;

  /// No description provided for @notifEmptyTitle.
  ///
  /// In vi, this message translates to:
  /// **'Chưa có thông báo'**
  String get notifEmptyTitle;

  /// No description provided for @notifEmptyBody.
  ///
  /// In vi, this message translates to:
  /// **'Nhắc hạn sử dụng và tổng kết chống lãng phí sẽ xuất hiện ở đây.'**
  String get notifEmptyBody;

  /// No description provided for @nearExpiryNotFound.
  ///
  /// In vi, this message translates to:
  /// **'Không tìm thấy nguyên liệu này trong kho.'**
  String get nearExpiryNotFound;

  /// No description provided for @nearExpiryMarkUsed.
  ///
  /// In vi, this message translates to:
  /// **'Đánh dấu đã dùng'**
  String get nearExpiryMarkUsed;

  /// No description provided for @nearExpirySeeSuggestions.
  ///
  /// In vi, this message translates to:
  /// **'Xem gợi ý'**
  String get nearExpirySeeSuggestions;

  /// No description provided for @expiryTipVeg.
  ///
  /// In vi, this message translates to:
  /// **'Rau ăn lá nên dùng trong ngày để giữ độ tươi và dinh dưỡng. Kiểm tra lá có bị úa hoặc nhũn không trước khi nấu.'**
  String get expiryTipVeg;

  /// No description provided for @expiryTipFruit.
  ///
  /// In vi, this message translates to:
  /// **'Trái cây chín nhanh ở nhiệt độ phòng. Cho vào ngăn mát để giữ thêm 2–3 ngày; dùng ngay khi vỏ bắt đầu nhăn.'**
  String get expiryTipFruit;

  /// No description provided for @expiryTipMeat.
  ///
  /// In vi, this message translates to:
  /// **'Thịt tươi để ngăn mát nên nấu trong 1–2 ngày. Nếu chưa dùng kịp, cấp đông ngay để giữ chất lượng.'**
  String get expiryTipMeat;

  /// No description provided for @expiryTipFish.
  ///
  /// In vi, this message translates to:
  /// **'Cá và hải sản rất nhanh hỏng — nấu trong ngày hoặc cấp đông. Ngửi thấy mùi tanh gắt thì nên bỏ.'**
  String get expiryTipFish;

  /// No description provided for @expiryTipDairy.
  ///
  /// In vi, this message translates to:
  /// **'Sữa và chế phẩm từ sữa giữ trong ngăn mát dưới 4°C. Dùng trước hạn và kiểm tra mùi trước khi uống.'**
  String get expiryTipDairy;

  /// No description provided for @expiryTipEgg.
  ///
  /// In vi, this message translates to:
  /// **'Trứng để ngăn mát dùng tốt trong vài tuần. Thử thả vào nước: trứng nổi là đã cũ.'**
  String get expiryTipEgg;

  /// No description provided for @expiryTipDefault.
  ///
  /// In vi, this message translates to:
  /// **'Ưu tiên dùng nguyên liệu này sớm. Luôn kiểm tra màu sắc, mùi và trạng thái thực phẩm trước khi chế biến.'**
  String get expiryTipDefault;

  /// No description provided for @settingsGroupAccount.
  ///
  /// In vi, this message translates to:
  /// **'Tài khoản'**
  String get settingsGroupAccount;

  /// No description provided for @settingsProfilePassword.
  ///
  /// In vi, this message translates to:
  /// **'Hồ sơ & mật khẩu'**
  String get settingsProfilePassword;

  /// No description provided for @settingsPlan.
  ///
  /// In vi, this message translates to:
  /// **'Gói dịch vụ'**
  String get settingsPlan;

  /// No description provided for @settingsPremiumSoon.
  ///
  /// In vi, this message translates to:
  /// **'Premium sắp có'**
  String get settingsPremiumSoon;

  /// No description provided for @settingsPantrySharing.
  ///
  /// In vi, this message translates to:
  /// **'Chia sẻ tủ bếp'**
  String get settingsPantrySharing;

  /// No description provided for @settingsGroupMealPlanning.
  ///
  /// In vi, this message translates to:
  /// **'Kế hoạch bữa ăn'**
  String get settingsGroupMealPlanning;

  /// No description provided for @settingsWasteReport.
  ///
  /// In vi, this message translates to:
  /// **'Báo cáo chống lãng phí'**
  String get settingsWasteReport;

  /// No description provided for @settingsGroupApp.
  ///
  /// In vi, this message translates to:
  /// **'Ứng dụng'**
  String get settingsGroupApp;

  /// No description provided for @settingsGroupOther.
  ///
  /// In vi, this message translates to:
  /// **'Khác'**
  String get settingsGroupOther;

  /// No description provided for @settingsAboutData.
  ///
  /// In vi, this message translates to:
  /// **'Giới thiệu & nguồn dữ liệu'**
  String get settingsAboutData;

  /// No description provided for @settingsSignOut.
  ///
  /// In vi, this message translates to:
  /// **'Đăng xuất'**
  String get settingsSignOut;

  /// No description provided for @signOutConfirmTitle.
  ///
  /// In vi, this message translates to:
  /// **'Đăng xuất?'**
  String get signOutConfirmTitle;

  /// No description provided for @signOutConfirmBody.
  ///
  /// In vi, this message translates to:
  /// **'Bạn sẽ cần đăng nhập lại để dùng SweepFood.'**
  String get signOutConfirmBody;

  /// No description provided for @planFullFree.
  ///
  /// In vi, this message translates to:
  /// **'Bản đầy đủ · miễn phí'**
  String get planFullFree;

  /// No description provided for @planPremiumDeveloping.
  ///
  /// In vi, this message translates to:
  /// **'Premium (đồng bộ, báo cáo nâng cao…) đang phát triển'**
  String get planPremiumDeveloping;

  /// No description provided for @planInterested.
  ///
  /// In vi, this message translates to:
  /// **'Quan tâm'**
  String get planInterested;

  /// No description provided for @aboutTitle.
  ///
  /// In vi, this message translates to:
  /// **'Giới thiệu & dữ liệu'**
  String get aboutTitle;

  /// No description provided for @aboutVersion.
  ///
  /// In vi, this message translates to:
  /// **'Phiên bản 1.0.0 (MVP)'**
  String get aboutVersion;

  /// No description provided for @aboutDataSources.
  ///
  /// In vi, this message translates to:
  /// **'Nguồn dữ liệu'**
  String get aboutDataSources;

  /// No description provided for @aboutNutritionData.
  ///
  /// In vi, this message translates to:
  /// **'Giá trị dinh dưỡng thực phẩm'**
  String get aboutNutritionData;

  /// No description provided for @aboutNutritionSource.
  ///
  /// In vi, this message translates to:
  /// **'Viện Dinh dưỡng QG'**
  String get aboutNutritionSource;

  /// No description provided for @aboutShelfLifeData.
  ///
  /// In vi, this message translates to:
  /// **'Thời gian bảo quản tham khảo'**
  String get aboutShelfLifeData;

  /// No description provided for @aboutDisclaimer.
  ///
  /// In vi, this message translates to:
  /// **'Thông tin dinh dưỡng và thời gian bảo quản chỉ mang tính ước tính, không thay thế tư vấn của chuyên gia dinh dưỡng hoặc y tế. Luôn kiểm tra màu sắc, mùi và trạng thái thực phẩm trước khi sử dụng.'**
  String get aboutDisclaimer;

  /// No description provided for @aboutRateApp.
  ///
  /// In vi, this message translates to:
  /// **'Đánh giá ứng dụng'**
  String get aboutRateApp;

  /// No description provided for @aboutThanks.
  ///
  /// In vi, this message translates to:
  /// **'Cảm ơn bạn!'**
  String get aboutThanks;

  /// No description provided for @notifSettingsTypesHeader.
  ///
  /// In vi, this message translates to:
  /// **'LOẠI THÔNG BÁO'**
  String get notifSettingsTypesHeader;

  /// No description provided for @notifTypeNearExpiry.
  ///
  /// In vi, this message translates to:
  /// **'Cảnh báo cận hạn'**
  String get notifTypeNearExpiry;

  /// No description provided for @notifTypeNearExpirySub.
  ///
  /// In vi, this message translates to:
  /// **'Khi nguyên liệu sắp hết hạn'**
  String get notifTypeNearExpirySub;

  /// No description provided for @notifTypeDailySuggestions.
  ///
  /// In vi, this message translates to:
  /// **'Gợi ý món hằng ngày'**
  String get notifTypeDailySuggestions;

  /// No description provided for @notifTypeWeeklyReport.
  ///
  /// In vi, this message translates to:
  /// **'Báo cáo tuần'**
  String get notifTypeWeeklyReport;

  /// No description provided for @notifTypePostCook.
  ///
  /// In vi, this message translates to:
  /// **'Nhắc sau khi nấu'**
  String get notifTypePostCook;

  /// No description provided for @notifTypePromos.
  ///
  /// In vi, this message translates to:
  /// **'Khuyến mãi & mẹo'**
  String get notifTypePromos;

  /// No description provided for @notifSettingsTiming.
  ///
  /// In vi, this message translates to:
  /// **'Thời điểm'**
  String get notifSettingsTiming;

  /// No description provided for @notifRemindAt.
  ///
  /// In vi, this message translates to:
  /// **'Nhắc cận hạn lúc'**
  String get notifRemindAt;

  /// No description provided for @notifDnd.
  ///
  /// In vi, this message translates to:
  /// **'Không làm phiền'**
  String get notifDnd;

  /// No description provided for @notifDndStart.
  ///
  /// In vi, this message translates to:
  /// **'Bắt đầu không làm phiền'**
  String get notifDndStart;

  /// No description provided for @notifDndEnd.
  ///
  /// In vi, this message translates to:
  /// **'Kết thúc không làm phiền'**
  String get notifDndEnd;

  /// No description provided for @pantrySharingIntro.
  ///
  /// In vi, this message translates to:
  /// **'Mời tối đa 4 người cùng xem và cập nhật tủ bếp. Mọi thay đổi được đồng bộ cho tất cả thành viên.'**
  String get pantrySharingIntro;

  /// No description provided for @pantrySharingFootnote.
  ///
  /// In vi, this message translates to:
  /// **'Thành viên có thể thêm, sửa, xóa nguyên liệu và xem gợi ý món. Chỉ chủ tủ bếp mới xóa được thành viên.'**
  String get pantrySharingFootnote;

  /// No description provided for @pantrySharingInvite.
  ///
  /// In vi, this message translates to:
  /// **'Mời thành viên'**
  String get pantrySharingInvite;

  /// No description provided for @pantryMemberInvited.
  ///
  /// In vi, this message translates to:
  /// **'Đã mời · chờ xác nhận'**
  String get pantryMemberInvited;

  /// No description provided for @pantryRoleOwner.
  ///
  /// In vi, this message translates to:
  /// **'Chủ tủ bếp'**
  String get pantryRoleOwner;

  /// No description provided for @pantryRoleEditor.
  ///
  /// In vi, this message translates to:
  /// **'Có thể chỉnh sửa'**
  String get pantryRoleEditor;

  /// No description provided for @profileGroupInfo.
  ///
  /// In vi, this message translates to:
  /// **'Thông tin'**
  String get profileGroupInfo;

  /// No description provided for @profileEditSoon.
  ///
  /// In vi, this message translates to:
  /// **'Sửa hồ sơ sẽ có ở bản sau.'**
  String get profileEditSoon;

  /// No description provided for @profileGroupSecurity.
  ///
  /// In vi, this message translates to:
  /// **'Bảo mật'**
  String get profileGroupSecurity;

  /// No description provided for @profileChangePassword.
  ///
  /// In vi, this message translates to:
  /// **'Đổi mật khẩu'**
  String get profileChangePassword;

  /// No description provided for @profileChangePasswordSoon.
  ///
  /// In vi, this message translates to:
  /// **'Đổi mật khẩu sẽ có ở bản sau.'**
  String get profileChangePasswordSoon;

  /// No description provided for @profileDeleteAccount.
  ///
  /// In vi, this message translates to:
  /// **'Xóa tài khoản'**
  String get profileDeleteAccount;

  /// No description provided for @profileDeleteConfirmTitle.
  ///
  /// In vi, this message translates to:
  /// **'Xóa tài khoản?'**
  String get profileDeleteConfirmTitle;

  /// No description provided for @profileDeleteConfirmBody.
  ///
  /// In vi, this message translates to:
  /// **'Toàn bộ dữ liệu tủ bếp sẽ bị xóa vĩnh viễn. Hành động này không thể hoàn tác.'**
  String get profileDeleteConfirmBody;

  /// No description provided for @profileDeleteRequested.
  ///
  /// In vi, this message translates to:
  /// **'Yêu cầu xóa tài khoản đã được ghi nhận.'**
  String get profileDeleteRequested;

  /// No description provided for @accountInfoSection.
  ///
  /// In vi, this message translates to:
  /// **'Thông tin'**
  String get accountInfoSection;

  /// No description provided for @accountSecuritySection.
  ///
  /// In vi, this message translates to:
  /// **'Bảo mật'**
  String get accountSecuritySection;

  /// No description provided for @accountSendCode.
  ///
  /// In vi, this message translates to:
  /// **'Gửi mã'**
  String get accountSendCode;

  /// No description provided for @accountVerifyCta.
  ///
  /// In vi, this message translates to:
  /// **'Xác nhận'**
  String get accountVerifyCta;

  /// No description provided for @editProfileTitle.
  ///
  /// In vi, this message translates to:
  /// **'Sửa hồ sơ'**
  String get editProfileTitle;

  /// No description provided for @editProfileNameLabel.
  ///
  /// In vi, this message translates to:
  /// **'Họ và tên'**
  String get editProfileNameLabel;

  /// No description provided for @editProfileSaved.
  ///
  /// In vi, this message translates to:
  /// **'Đã cập nhật hồ sơ.'**
  String get editProfileSaved;

  /// No description provided for @changePasswordTitle.
  ///
  /// In vi, this message translates to:
  /// **'Đổi mật khẩu'**
  String get changePasswordTitle;

  /// No description provided for @changePasswordIntro.
  ///
  /// In vi, this message translates to:
  /// **'Chúng tôi sẽ gửi mã xác thực 6 chữ số tới số {phone}.'**
  String changePasswordIntro(String phone);

  /// No description provided for @changePasswordOtpHint.
  ///
  /// In vi, this message translates to:
  /// **'Nhập mã xác thực và mật khẩu mới.'**
  String get changePasswordOtpHint;

  /// No description provided for @changePasswordNewLabel.
  ///
  /// In vi, this message translates to:
  /// **'Mật khẩu mới'**
  String get changePasswordNewLabel;

  /// No description provided for @changePasswordDone.
  ///
  /// In vi, this message translates to:
  /// **'Đã đổi mật khẩu. Vui lòng đăng nhập lại.'**
  String get changePasswordDone;

  /// No description provided for @changeEmailTitle.
  ///
  /// In vi, this message translates to:
  /// **'Đổi email'**
  String get changeEmailTitle;

  /// No description provided for @changeEmailIntro.
  ///
  /// In vi, this message translates to:
  /// **'Nhập email mới. Mã xác thực sẽ được gửi tới địa chỉ đó.'**
  String get changeEmailIntro;

  /// No description provided for @changeEmailNewLabel.
  ///
  /// In vi, this message translates to:
  /// **'Email mới'**
  String get changeEmailNewLabel;

  /// No description provided for @changeEmailOtpHint.
  ///
  /// In vi, this message translates to:
  /// **'Nhập mã đã gửi tới {email}.'**
  String changeEmailOtpHint(String email);

  /// No description provided for @changeEmailDone.
  ///
  /// In vi, this message translates to:
  /// **'Đã cập nhật email.'**
  String get changeEmailDone;

  /// No description provided for @changePhoneTitle.
  ///
  /// In vi, this message translates to:
  /// **'Đổi số điện thoại'**
  String get changePhoneTitle;

  /// No description provided for @changePhoneIntro.
  ///
  /// In vi, this message translates to:
  /// **'Nhập số điện thoại mới. Mã xác thực sẽ được gửi tới số đó.'**
  String get changePhoneIntro;

  /// No description provided for @changePhoneNewLabel.
  ///
  /// In vi, this message translates to:
  /// **'Số điện thoại mới'**
  String get changePhoneNewLabel;

  /// No description provided for @changePhoneOtpHint.
  ///
  /// In vi, this message translates to:
  /// **'Nhập mã đã gửi tới {phone}.'**
  String changePhoneOtpHint(String phone);

  /// No description provided for @changePhoneDone.
  ///
  /// In vi, this message translates to:
  /// **'Đã cập nhật số điện thoại.'**
  String get changePhoneDone;

  /// No description provided for @minutesLabel.
  ///
  /// In vi, this message translates to:
  /// **'{minutes} phút'**
  String minutesLabel(int minutes);

  /// No description provided for @dishMetaPrep.
  ///
  /// In vi, this message translates to:
  /// **'{minutes} phút chuẩn bị'**
  String dishMetaPrep(int minutes);

  /// No description provided for @dishMetaKcalPerServing.
  ///
  /// In vi, this message translates to:
  /// **'{kcal} kcal / khẩu phần'**
  String dishMetaKcalPerServing(int kcal);

  /// No description provided for @shoppingTitle.
  ///
  /// In vi, this message translates to:
  /// **'Danh sách mua sắm'**
  String get shoppingTitle;

  /// No description provided for @shoppingAddItem.
  ///
  /// In vi, this message translates to:
  /// **'Thêm món'**
  String get shoppingAddItem;

  /// No description provided for @shoppingEmptyTitle.
  ///
  /// In vi, this message translates to:
  /// **'Chưa có danh sách mua sắm'**
  String get shoppingEmptyTitle;

  /// No description provided for @shoppingEmptyBody.
  ///
  /// In vi, this message translates to:
  /// **'Lập thực đơn tuần rồi tạo danh sách mua sắm chỉ với 1 chạm.'**
  String get shoppingEmptyBody;

  /// No description provided for @shoppingPlanWeek.
  ///
  /// In vi, this message translates to:
  /// **'Lập thực đơn tuần'**
  String get shoppingPlanWeek;

  /// No description provided for @shoppingShowInStock.
  ///
  /// In vi, this message translates to:
  /// **'Hiện nguyên liệu đã có trong kho'**
  String get shoppingShowInStock;

  /// No description provided for @shoppingEstimate.
  ///
  /// In vi, this message translates to:
  /// **'Ước tính'**
  String get shoppingEstimate;

  /// No description provided for @shoppingToBuyCount.
  ///
  /// In vi, this message translates to:
  /// **'{count} nguyên liệu cần mua'**
  String shoppingToBuyCount(int count);

  /// No description provided for @shoppingItemName.
  ///
  /// In vi, this message translates to:
  /// **'Tên món'**
  String get shoppingItemName;

  /// No description provided for @shoppingAddToList.
  ///
  /// In vi, this message translates to:
  /// **'Thêm vào danh sách'**
  String get shoppingAddToList;

  /// No description provided for @shoppingHavePill.
  ///
  /// In vi, this message translates to:
  /// **'đã có'**
  String get shoppingHavePill;

  /// No description provided for @shoppingFromRecipe.
  ///
  /// In vi, this message translates to:
  /// **'Từ công thức'**
  String get shoppingFromRecipe;

  /// No description provided for @shoppingPurchaseTitle.
  ///
  /// In vi, this message translates to:
  /// **'Xác nhận đã mua'**
  String get shoppingPurchaseTitle;

  /// No description provided for @shoppingPurchaseSubtitle.
  ///
  /// In vi, this message translates to:
  /// **'Thông tin này giúp lưu vào kho ngay khi bạn tick đã mua.'**
  String get shoppingPurchaseSubtitle;

  /// No description provided for @shoppingPurchaseExpiryPick.
  ///
  /// In vi, this message translates to:
  /// **'Chọn hạn sử dụng'**
  String get shoppingPurchaseExpiryPick;

  /// No description provided for @shoppingPurchasePriceLabel.
  ///
  /// In vi, this message translates to:
  /// **'Giá (VNĐ, tùy chọn)'**
  String get shoppingPurchasePriceLabel;

  /// No description provided for @shoppingPurchaseConfirm.
  ///
  /// In vi, this message translates to:
  /// **'Xác nhận'**
  String get shoppingPurchaseConfirm;

  /// No description provided for @subCurrentPlan.
  ///
  /// In vi, this message translates to:
  /// **'Bạn đang dùng'**
  String get subCurrentPlan;

  /// No description provided for @subInterestRegistered.
  ///
  /// In vi, this message translates to:
  /// **'Đã đăng ký quan tâm Premium'**
  String get subInterestRegistered;

  /// No description provided for @subInterestCta.
  ///
  /// In vi, this message translates to:
  /// **'Quan tâm Premium — báo tôi khi ra mắt'**
  String get subInterestCta;

  /// No description provided for @subDisclaimer.
  ///
  /// In vi, this message translates to:
  /// **'Trong giai đoạn thử nghiệm, tất cả tính năng đang miễn phí. Sau này một số tính năng nâng cao (đồng bộ nhiều thiết bị, chia sẻ tủ bếp, báo cáo chi tiết) sẽ chuyển sang gói Premium — bạn sẽ được báo trước.'**
  String get subDisclaimer;

  /// No description provided for @subTierFree.
  ///
  /// In vi, this message translates to:
  /// **'Bản đầy đủ · miễn phí'**
  String get subTierFree;

  /// No description provided for @subTierMonthly.
  ///
  /// In vi, this message translates to:
  /// **'Premium tháng'**
  String get subTierMonthly;

  /// No description provided for @subTierYearly.
  ///
  /// In vi, this message translates to:
  /// **'Premium năm'**
  String get subTierYearly;

  /// No description provided for @subTierFamily.
  ///
  /// In vi, this message translates to:
  /// **'Premium gia đình'**
  String get subTierFamily;

  /// No description provided for @paywallTitle.
  ///
  /// In vi, this message translates to:
  /// **'SweepFood Premium sắp ra mắt'**
  String get paywallTitle;

  /// No description provided for @paywallSubtitle.
  ///
  /// In vi, this message translates to:
  /// **'Hiện tại bạn đang dùng miễn phí tất cả tính năng. Đăng ký để được báo khi Premium chính thức và nhận ưu đãi sớm.'**
  String get paywallSubtitle;

  /// No description provided for @paywallBenefit1.
  ///
  /// In vi, this message translates to:
  /// **'Kho nguyên liệu không giới hạn'**
  String get paywallBenefit1;

  /// No description provided for @paywallBenefit2.
  ///
  /// In vi, this message translates to:
  /// **'Quét tem & hóa đơn không giới hạn'**
  String get paywallBenefit2;

  /// No description provided for @paywallBenefit3.
  ///
  /// In vi, this message translates to:
  /// **'Lập thực đơn tuần & danh sách mua sắm'**
  String get paywallBenefit3;

  /// No description provided for @paywallBenefit4.
  ///
  /// In vi, this message translates to:
  /// **'Mục tiêu dinh dưỡng theo ngày'**
  String get paywallBenefit4;

  /// No description provided for @paywallBenefit5.
  ///
  /// In vi, this message translates to:
  /// **'Báo cáo thực phẩm đã tiết kiệm'**
  String get paywallBenefit5;

  /// No description provided for @paywallBenefit6.
  ///
  /// In vi, this message translates to:
  /// **'Chia sẻ tủ bếp cho tối đa 4 người'**
  String get paywallBenefit6;

  /// No description provided for @paywallSubmitted.
  ///
  /// In vi, this message translates to:
  /// **'Đã ghi nhận — cảm ơn bạn!'**
  String get paywallSubmitted;

  /// No description provided for @paywallNotifyMe.
  ///
  /// In vi, this message translates to:
  /// **'Nhận thông báo khi ra mắt'**
  String get paywallNotifyMe;

  /// No description provided for @paywallFinePrint.
  ///
  /// In vi, this message translates to:
  /// **'Chưa tính phí · giá & gói đang trong giai đoạn kiểm chứng'**
  String get paywallFinePrint;

  /// No description provided for @favoritesTitle.
  ///
  /// In vi, this message translates to:
  /// **'Món & thực đơn yêu thích'**
  String get favoritesTitle;

  /// No description provided for @favAddToMenuTitle.
  ///
  /// In vi, this message translates to:
  /// **'Thêm vào thực đơn mẫu'**
  String get favAddToMenuTitle;
}

class _AppL10nDelegate extends LocalizationsDelegate<AppL10n> {
  const _AppL10nDelegate();

  @override
  Future<AppL10n> load(Locale locale) {
    return SynchronousFuture<AppL10n>(lookupAppL10n(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'vi'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppL10nDelegate old) => false;
}

AppL10n lookupAppL10n(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppL10nEn();
    case 'vi':
      return AppL10nVi();
  }

  throw FlutterError(
    'AppL10n.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
