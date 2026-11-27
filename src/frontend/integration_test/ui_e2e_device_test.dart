import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sweepfood/app/app.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/config/app_config.dart';
import 'package:sweepfood/core/config/app_config_provider.dart';
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/core/config/flavor.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/core/widgets/app_logo.dart';
import 'package:sweepfood/core/widgets/recipe_image.dart';
import 'package:sweepfood/features/auth/domain/entities/session.dart';
import 'package:sweepfood/features/auth/domain/entities/user.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/features/auth/presentation/screens/welcome_screen.dart';
import 'package:sweepfood/features/dishes/presentation/screens/dish_detail_screen.dart';
import 'package:sweepfood/features/home/presentation/screens/home_screen.dart';
import 'package:sweepfood/features/pantry/presentation/screens/pantry_item_detail_screen.dart';
import 'package:sweepfood/features/pantry/presentation/screens/pantry_screen.dart';
import 'package:sweepfood/features/settings/presentation/screens/preferences_screen.dart';
import 'package:sweepfood/features/settings/presentation/screens/settings_home_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

class _DeviceMockSessionController extends SessionController {
  @override
  Future<Session?> build() async => const Session(
    user: User(id: 'device-test-user', phone: '+84901234567', name: 'Minh'),
    accessToken: 'device-mock-token',
    refreshToken: 'device-mock-refresh',
  );
}

Future<void> _pumpUntilFound(
  WidgetTester tester,
  Finder finder, {
  int maxPumps = 25,
}) async {
  for (var i = 0; i < maxPumps; i++) {
    await tester.pump(const Duration(milliseconds: 200));
    if (finder.evaluate().isNotEmpty) return;
  }
}

Future<void> _settleBounded(WidgetTester tester, {int steps = 6}) async {
  for (var i = 0; i < steps; i++) {
    await tester.pump(const Duration(milliseconds: 200));
  }
}

Finder _navTab(String label) =>
    find.descendant(of: find.byType(NavigationBar), matching: find.text(label));

Future<void> _tapBack(WidgetTester tester) async {
  final backBtn = find.byType(BackButton).hitTestable();
  if (backBtn.evaluate().isNotEmpty) {
    await tester.tap(backBtn.last);
  } else {
    final backIcon = find.byType(BackButtonIcon).hitTestable();
    await tester.tap(backIcon.last);
  }
}

Finder _verticalScrollableOf(Type screenType) => find.descendant(
  of: find.byType(screenType),
  matching: find.byWidgetPredicate(
    (w) => w is Scrollable && w.axisDirection == AxisDirection.down,
  ),
);

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Welcome carousel renders SVG slides smoothly on device', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('vi'),
        supportedLocales: AppL10n.supportedLocales,
        localizationsDelegates: AppL10n.localizationsDelegates,
        theme: AppTheme.light,
        darkTheme: AppTheme.dark,
        home: const WelcomeScreen(),
      ),
    );
    await _settleBounded(tester);

    expect(find.byType(AppLogo), findsOneWidget);
    expect(find.text('SweepFood'), findsOneWidget);
    expect(find.text('Biến nguyên liệu đang có thành bữa ăn'), findsOneWidget);

    await tester.drag(find.byType(PageView), const Offset(-320, 0));
    await _settleBounded(tester);
    expect(find.text('Gợi ý món hợp tủ bếp của bạn'), findsOneWidget);

    await tester.drag(find.byType(PageView), const Offset(-320, 0));
    await _settleBounded(tester);
    expect(find.text('Nấu hết đồ, bớt lãng phí'), findsOneWidget);

    expect(tester.takeException(), isNull);
  });

  testWidgets('Full UI E2E flow across all 5 tabs and Dark Mode on device', (
    tester,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(AppConstants.kOnboardingDone, true);
    await prefs.remove('app.theme_mode');

    const deviceConfig = AppConfig(
      flavor: Flavor.dev,
      backend: Backend.mock,
      apiBaseUrl: 'http://127.0.0.1:4000/api',
      premiumEnabled: false,
      nearExpiryDays: 3,
      fcmEnabled: false,
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          appConfigProvider.overrideWithValue(deviceConfig),
          sharedPreferencesProvider.overrideWithValue(prefs),
          sessionControllerProvider.overrideWith(
            _DeviceMockSessionController.new,
          ),
        ],
        child: const SweepFoodApp(),
      ),
    );

    // 1. Home Dashboard
    await _pumpUntilFound(tester, find.text('Hôm nay ăn gì?').hitTestable());
    await _settleBounded(tester, steps: 5);
    expect(find.byType(AppLogo).hitTestable(), findsOneWidget);
    expect(find.text('Hôm nay ăn gì?').hitTestable(), findsOneWidget);
    expect(find.text('Nhịp bếp hôm nay').hitTestable(), findsOneWidget);
    await tester.scrollUntilVisible(
      find.text('CẦN DÙNG SỚM'),
      200,
      scrollable: _verticalScrollableOf(HomeScreen).first,
    );
    expect(find.text('CẦN DÙNG SỚM').hitTestable(), findsOneWidget);
    expect(tester.takeException(), isNull);

    // 2. Pantry tab + detail + FreshCheck banner
    await tester.tap(_navTab('Kho'));
    await _pumpUntilFound(tester, find.text('Kho thực phẩm').hitTestable());
    await _settleBounded(tester, steps: 4);
    expect(find.text('Kho thực phẩm').hitTestable(), findsOneWidget);
    await tester.scrollUntilVisible(
      find.text('Cải bó xôi'),
      200,
      scrollable: _verticalScrollableOf(PantryScreen).first,
    );
    expect(find.text('Cải bó xôi').hitTestable(), findsWidgets);

    await tester.tap(find.text('Cải bó xôi').hitTestable().first);
    await _pumpUntilFound(
      tester,
      find.text('Kiểm tra độ tươi ngay').hitTestable(),
    );
    await _settleBounded(tester, steps: 4);
    expect(find.text('Kiểm tra độ tươi ngay').hitTestable(), findsOneWidget);
    await tester.scrollUntilVisible(
      find.text('Chi tiết'),
      200,
      scrollable: _verticalScrollableOf(PantryItemDetailScreen).first,
    );
    expect(find.text('Chi tiết').hitTestable(), findsOneWidget);
    expect(tester.takeException(), isNull);

    await _tapBack(tester);
    await _settleBounded(tester, steps: 4);

    // 3. Suggestions tab + filter chips + DishDetail + Guided Cook Mode
    await tester.tap(_navTab('Gợi ý'));
    await _pumpUntilFound(tester, find.text('Salad bơ ức gà').hitTestable());
    await _settleBounded(tester, steps: 4);
    expect(find.text('Salad bơ ức gà').hitTestable(), findsWidgets);

    await tester.tap(find.text('Cứu đồ cận hạn').hitTestable().first);
    await _settleBounded(tester, steps: 2);
    await tester.tap(find.text('Tất cả').hitTestable().first);
    await _settleBounded(tester, steps: 2);

    await tester.tap(find.text('Salad bơ ức gà').hitTestable().first);
    await _pumpUntilFound(tester, find.text('Đã nấu món này').hitTestable());
    await _settleBounded(tester, steps: 4);
    expect(find.byType(RecipeImage).hitTestable(), findsWidgets);
    expect(find.text('Đã nấu món này').hitTestable(), findsOneWidget);

    // Scroll to Guided Cook Mode & start timer
    await tester.scrollUntilVisible(
      find.text('Chế độ nấu từng bước'),
      250,
      scrollable: _verticalScrollableOf(DishDetailScreen).first,
    );
    await tester.tap(find.text('Chế độ nấu từng bước').hitTestable().first);
    await _pumpUntilFound(tester, find.textContaining('Bước 1/').hitTestable());
    await _settleBounded(tester, steps: 3);
    expect(find.textContaining('Bước 1/').hitTestable(), findsWidgets);

    // Close Guided Cook sheet & navigate back to Suggestions
    await tester.tapAt(const Offset(20, 120));
    await _settleBounded(tester, steps: 3);
    await _tapBack(tester);
    await _settleBounded(tester, steps: 4);

    // 4. Shopping tab
    await tester.tap(_navTab('Mua sắm'));
    await _pumpUntilFound(tester, find.text('Danh sách mua sắm').hitTestable());
    await _settleBounded(tester, steps: 4);
    expect(find.text('Danh sách mua sắm').hitTestable(), findsOneWidget);
    expect(tester.takeException(), isNull);

    // 5. Profile tab -> Meal Plan Day-Strip -> Reports -> Dark Mode switch
    await tester.tap(_navTab('Cá nhân'));
    await _pumpUntilFound(tester, find.text('Thực đơn tuần').hitTestable());
    await _settleBounded(tester, steps: 3);

    await tester.tap(find.text('Thực đơn tuần').hitTestable().first);
    await _pumpUntilFound(tester, find.text('T5').hitTestable());
    await _settleBounded(tester, steps: 4);
    await tester.tap(find.text('T5').hitTestable().first);
    await _settleBounded(tester, steps: 2);
    expect(tester.takeException(), isNull);
    await _tapBack(tester);
    await _settleBounded(tester, steps: 3);

    await tester.scrollUntilVisible(
      find.text('Báo cáo chống lãng phí'),
      200,
      scrollable: _verticalScrollableOf(SettingsHomeScreen).first,
    );
    await tester.tap(find.text('Báo cáo chống lãng phí').hitTestable().first);
    await _pumpUntilFound(tester, find.text('Chống lãng phí').hitTestable());
    await _settleBounded(tester, steps: 4);
    expect(tester.takeException(), isNull);
    await _tapBack(tester);
    await _settleBounded(tester, steps: 3);

    // Switch to Dark Mode & verify Home renders cleanly in Dark Mode on device
    await tester.scrollUntilVisible(
      find.text('Tùy chọn'),
      200,
      scrollable: _verticalScrollableOf(SettingsHomeScreen).first,
    );
    await tester.tap(find.text('Tùy chọn').hitTestable().first);
    await _pumpUntilFound(tester, find.text('Chủ đề').hitTestable());
    await _settleBounded(tester, steps: 2);
    await tester.tap(find.text('Chủ đề').hitTestable().first);
    await _pumpUntilFound(tester, find.text('Tối').hitTestable());
    await tester.tap(find.text('Tối').hitTestable().first);
    await _settleBounded(tester, steps: 3);
    expect(
      Theme.of(tester.element(find.byType(PreferencesScreen))).brightness,
      Brightness.dark,
    );

    await _tapBack(tester);
    await _settleBounded(tester, steps: 3);
    await tester.tap(_navTab('Trang chủ'));
    await _pumpUntilFound(tester, find.byType(HomeScreen).hitTestable());
    await tester.scrollUntilVisible(
      find.text('Hôm nay ăn gì?'),
      -250,
      scrollable: _verticalScrollableOf(HomeScreen).first,
    );
    await _settleBounded(tester, steps: 3);
    expect(find.byType(AppLogo).hitTestable(), findsOneWidget);
    expect(find.text('Hôm nay ăn gì?').hitTestable(), findsOneWidget);
    expect(
      Theme.of(tester.element(find.byType(HomeScreen))).brightness,
      Brightness.dark,
    );
    expect(tester.takeException(), isNull);
  });
}
