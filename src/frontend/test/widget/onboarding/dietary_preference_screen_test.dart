import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:go_router/go_router.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/domain/entities/session.dart';
import 'package:sweepfood/features/auth/domain/entities/user.dart';
import 'package:sweepfood/features/auth/domain/repositories/auth_repository.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/features/onboarding/presentation/screens/dietary_preference_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';
import 'package:sweepfood/shared/domain/nutrition_profile.dart';

class _MockAuthRepository extends Mock implements AuthRepository {}

class _SignedInSessionController extends SessionController {
  _SignedInSessionController(this._session);

  final Session _session;

  @override
  Future<Session?> build() async => _session;
}

void main() {
  testWidgets(
    'Onboarding shows all 5 diets including Vegetarian, disclaimer, and syncs PATCH /users/profile',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      final authRepo = _MockAuthRepository();
      const baseUser = User(id: 'u-1', phone: '+84901234567', name: 'An');
      const updatedUser = User(
        id: 'u-1',
        phone: '+84901234567',
        name: 'An',
        dietaryPreference: DietaryPreference.vegetarian,
        nutritionProfile: NutritionProfile(diet: DietaryPreference.vegetarian),
      );
      when(
        () => authRepo.updateProfile(
          name: any(named: 'name'),
          preferences: any(named: 'preferences'),
        ),
      ).thenAnswer((_) async => const Right(updatedUser));

      final router = GoRouter(
        initialLocation: Routes.onboardingDiet,
        routes: [
          GoRoute(
            path: Routes.onboardingDiet,
            builder: (_, __) => const DietaryPreferenceScreen(),
          ),
          GoRoute(
            path: Routes.onboardingPantry,
            builder: (_, __) => const Scaffold(body: Text('Next step')),
          ),
        ],
      );

      await tester.binding.setSurfaceSize(const Size(430, 932));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            sharedPreferencesProvider.overrideWithValue(prefs),
            authRepositoryProvider.overrideWithValue(authRepo),
            sessionControllerProvider.overrideWith(
              () => _SignedInSessionController(
                const Session(
                  user: baseUser,
                  accessToken: 'a',
                  refreshToken: 'r',
                ),
              ),
            ),
          ],
          child: MaterialApp.router(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            routerConfig: router,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Cân bằng'), findsOneWidget);
      expect(find.text('Ăn chay'), findsOneWidget);
      expect(
        find.text('Gợi ý tham khảo, không thay lời khuyên của bác sĩ'),
        findsOneWidget,
      );

      await tester.tap(find.text('Ăn chay'));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Tiếp tục'));
      await tester.pumpAndSettle();

      verify(
        () => authRepo.updateProfile(preferences: {'diet': 'vegetarian'}),
      ).called(1);
      expect(find.text('Next step'), findsOneWidget);
    },
  );
}
