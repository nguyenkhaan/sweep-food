import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/domain/entities/session.dart';
import 'package:sweepfood/features/auth/domain/entities/user.dart';
import 'package:sweepfood/features/auth/domain/repositories/auth_repository.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/features/settings/presentation/screens/nutrition_profile_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';
import 'package:sweepfood/shared/domain/nutrition_profile.dart';

class _MockAuthRepository extends Mock implements AuthRepository {}

class _FakeSessionController extends SessionController {
  _FakeSessionController(this._session);

  final Session _session;

  @override
  Future<Session?> build() async => _session;
}

void main() {
  testWidgets(
    'NutritionProfileScreen loads saved profile, edits all 5 sections, and saves via PATCH /users/profile (dark theme)',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      final authRepo = _MockAuthRepository();

      const initialProfile = NutritionProfile(
        householdSize: 2,
        diet: DietaryPreference.moreVeg,
        healthConditions: [HealthCondition.hypertension],
        allergies: [AllergyGroup.shellfish],
        dislikedIngredients: ['rau mùi'],
      );
      const initialUser = User(
        id: 'u-1',
        phone: '+84901234567',
        name: 'Minh',
        dietaryPreference: DietaryPreference.moreVeg,
        nutritionProfile: initialProfile,
      );

      Map<String, dynamic>? capturedPreferences;
      when(
        () => authRepo.updateProfile(
          name: any(named: 'name'),
          preferences: any(named: 'preferences'),
        ),
      ).thenAnswer((invocation) async {
        capturedPreferences =
            invocation.namedArguments[#preferences] as Map<String, dynamic>?;
        final savedProfile = NutritionProfile.fromPreferencesMap(
          capturedPreferences ?? const {},
        );
        return Right(
          initialUser.copyWith(
            dietaryPreference: savedProfile.diet,
            nutritionProfile: savedProfile,
          ),
        );
      });

      await tester.binding.setSurfaceSize(const Size(430, 1400));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            sharedPreferencesProvider.overrideWithValue(prefs),
            authRepositoryProvider.overrideWithValue(authRepo),
            sessionControllerProvider.overrideWith(
              () => _FakeSessionController(
                const Session(
                  user: initialUser,
                  accessToken: 'a',
                  refreshToken: 'r',
                ),
              ),
            ),
          ],
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            darkTheme: AppTheme.dark,
            themeMode: ThemeMode.dark,
            home: const NutritionProfileScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Disclaimer & initial values are rendered.
      expect(
        find.text('Gợi ý tham khảo, không thay lời khuyên của bác sĩ'),
        findsOneWidget,
      );
      expect(find.text('2'), findsOneWidget);
      expect(find.text('Ăn chay'), findsOneWidget);

      // Increment household size to 3 and pick Vegetarian.
      await tester.tap(find.byIcon(Icons.add_rounded));
      await tester.pumpAndSettle();
      expect(find.text('3'), findsOneWidget);

      await tester.tap(find.text('Ăn chay'));
      await tester.pumpAndSettle();

      // Scroll down to toggle a health condition, allergy, and add a disliked item.
      final scrollable = find.byType(Scrollable).first;
      await tester.scrollUntilVisible(
        find.text('Tiểu đường'),
        300,
        scrollable: scrollable,
      );
      await tester.tap(find.text('Tiểu đường'));
      await tester.pumpAndSettle();

      await tester.scrollUntilVisible(
        find.text('Đậu phộng'),
        300,
        scrollable: scrollable,
      );
      await tester.tap(find.text('Đậu phộng'));
      await tester.pumpAndSettle();

      await tester.scrollUntilVisible(
        find.text('rau mùi'),
        300,
        scrollable: scrollable,
      );
      expect(find.text('rau mùi'), findsOneWidget);

      await tester.enterText(find.byType(TextField), 'Hành tây');
      await tester.tap(find.text('Thêm'));
      await tester.pumpAndSettle();
      expect(find.text('Hành tây'), findsOneWidget);

      // Save profile via sticky bottom CTA.
      await tester.tap(find.text('Lưu hồ sơ ăn uống'));
      await tester.pumpAndSettle();

      expect(capturedPreferences, {
        'household_size': 3,
        'diet': 'vegetarian',
        'health_conditions': ['nguoi_cao_huyet_ap', 'nguoi_tieu_duong'],
        'allergies': ['shellfish', 'peanut'],
        'disliked_ingredients': ['rau mùi', 'Hành tây'],
      });
    },
  );
}
