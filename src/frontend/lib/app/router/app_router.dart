import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/app/router/route_guards.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/shell/app_shell.dart';
import 'package:sweepfood/features/auth/presentation/screens/forgot_password_screen.dart';
import 'package:sweepfood/features/auth/presentation/screens/login_screen.dart';
import 'package:sweepfood/features/auth/presentation/screens/otp_screen.dart';
import 'package:sweepfood/features/auth/presentation/screens/register_screen.dart';
import 'package:sweepfood/features/auth/presentation/screens/reset_password_screen.dart';
import 'package:sweepfood/features/auth/presentation/screens/splash_screen.dart';
import 'package:sweepfood/features/auth/presentation/screens/welcome_screen.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_result.dart';
import 'package:sweepfood/features/cooking/presentation/screens/cook_result_screen.dart';
import 'package:sweepfood/features/dishes/presentation/screens/dish_detail_screen.dart';
import 'package:sweepfood/features/home/presentation/screens/home_screen.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';
import 'package:sweepfood/features/ingest/presentation/screens/camera_capture_screen.dart';
import 'package:sweepfood/features/ingest/presentation/screens/label_review_screen.dart';
import 'package:sweepfood/features/ingest/presentation/screens/receipt_review_screen.dart';
import 'package:sweepfood/features/ingest/presentation/screens/scan_failed_screen.dart';
import 'package:sweepfood/features/ingest/presentation/screens/voice_capture_screen.dart';
import 'package:sweepfood/features/ingest/presentation/screens/voice_review_screen.dart';
import 'package:sweepfood/features/meal_plan/presentation/screens/meal_plan_screen.dart';
import 'package:sweepfood/features/notifications/presentation/screens/notification_center_screen.dart';
import 'package:sweepfood/features/onboarding/presentation/screens/dietary_preference_screen.dart';
import 'package:sweepfood/features/onboarding/presentation/screens/onboarding_pantry_screen.dart';
import 'package:sweepfood/features/pantry/presentation/screens/add_ingredient_screen.dart';
import 'package:sweepfood/features/pantry/presentation/screens/pantry_item_detail_screen.dart';
import 'package:sweepfood/features/pantry/presentation/screens/pantry_screen.dart';
import 'package:sweepfood/features/reports/presentation/screens/reports_screen.dart';
import 'package:sweepfood/features/settings/presentation/screens/about_screen.dart';
import 'package:sweepfood/features/settings/presentation/screens/notification_settings_screen.dart';
import 'package:sweepfood/features/settings/presentation/screens/pantry_sharing_screen.dart';
import 'package:sweepfood/features/settings/presentation/screens/preferences_screen.dart';
import 'package:sweepfood/features/settings/presentation/screens/profile_screen.dart';
import 'package:sweepfood/features/settings/presentation/screens/settings_home_screen.dart';
import 'package:sweepfood/features/shopping_list/presentation/screens/shopping_list_screen.dart';
import 'package:sweepfood/features/subscription/presentation/screens/paywall_screen.dart';
import 'package:sweepfood/features/subscription/presentation/screens/subscription_screen.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/presentation/screens/suggestion_list_screen.dart';

part 'app_router.g.dart';

final _rootKey = GlobalKey<NavigatorState>(debugLabel: 'root');
final _homeKey = GlobalKey<NavigatorState>(debugLabel: 'home');
final _pantryKey = GlobalKey<NavigatorState>(debugLabel: 'pantry');
final _suggestionsKey = GlobalKey<NavigatorState>(debugLabel: 'suggestions');
final _shoppingKey = GlobalKey<NavigatorState>(debugLabel: 'shopping');
final _profileKey = GlobalKey<NavigatorState>(debugLabel: 'profile');

/// The app's [GoRouter], provided via Riverpod so redirects can react to auth
/// state (from M5). Kept alive for the app's lifetime.
@Riverpod(keepAlive: true)
GoRouter appRouter(Ref ref) {
  return GoRouter(
    navigatorKey: _rootKey,
    initialLocation: Routes.initialLocation,
    debugLogDiagnostics: true,
    refreshListenable: AuthRouterRefresh(ref),
    redirect: (context, state) => appRedirect(ref, context, state),
    routes: [
      GoRoute(
        path: Routes.splash,
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: Routes.welcome,
        builder: (context, state) => const WelcomeScreen(),
      ),
      GoRoute(
        path: Routes.login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: Routes.register,
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: Routes.verifyOtp,
        builder: (context, state) => OtpScreen(args: state.extra as OtpArgs?),
      ),
      GoRoute(
        path: Routes.forgotPassword,
        builder: (context, state) => const ForgotPasswordScreen(),
      ),
      GoRoute(
        path: Routes.resetPassword,
        builder: (context, state) =>
            ResetPasswordScreen(args: state.extra as ResetPasswordArgs?),
      ),
      GoRoute(
        path: Routes.onboardingDiet,
        builder: (context, state) => const DietaryPreferenceScreen(),
      ),
      GoRoute(
        path: Routes.onboardingPantry,
        builder: (context, state) => const OnboardingPantryScreen(),
      ),
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) =>
            AppShell(navigationShell: navigationShell),
        branches: [
          StatefulShellBranch(
            navigatorKey: _homeKey,
            routes: [
              GoRoute(
                path: Routes.home,
                builder: (context, state) => const HomeScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            navigatorKey: _pantryKey,
            routes: [
              GoRoute(
                path: Routes.pantry,
                builder: (context, state) => const PantryScreen(),
                routes: [
                  GoRoute(
                    path: Routes.addIngredient, // '/pantry/add'
                    parentNavigatorKey: _rootKey,
                    builder: (context, state) =>
                        AddIngredientScreen(editItemId: state.extra as String?),
                  ),
                  GoRoute(
                    path: Routes.pantryItem, // '/pantry/item/:id'
                    parentNavigatorKey: _rootKey,
                    builder: (context, state) => PantryItemDetailScreen(
                      itemId: state.pathParameters['id']!,
                    ),
                  ),
                  GoRoute(
                    path: Routes.scanCamera, // '/pantry/scan/camera'
                    parentNavigatorKey: _rootKey,
                    builder: (context, state) {
                      final modeQuery = state.uri.queryParameters['mode'];
                      final initialMode = modeQuery == 'receipt'
                          ? CameraScanMode.receipt
                          : CameraScanMode.label;
                      return CameraCaptureScreen(initialMode: initialMode);
                    },
                  ),
                  GoRoute(
                    path: Routes.scanLabelReview, // '/pantry/scan/label-review'
                    parentNavigatorKey: _rootKey,
                    builder: (context, state) => LabelReviewScreen(
                      job: state.extra as ScanJob? ??
                          const ScanJob(id: 'manual', type: ScanType.label),
                    ),
                  ),
                  GoRoute(
                    path: Routes.scanReceiptReview, // '/pantry/scan/receipt-review'
                    parentNavigatorKey: _rootKey,
                    builder: (context, state) => ReceiptReviewScreen(
                      job: state.extra as ScanJob? ??
                          const ScanJob(id: 'manual', type: ScanType.receipt),
                    ),
                  ),
                  GoRoute(
                    path: Routes.scanVoiceCapture, // '/pantry/scan/voice-capture'
                    parentNavigatorKey: _rootKey,
                    builder: (context, state) => const VoiceCaptureScreen(),
                  ),
                  GoRoute(
                    path: Routes.scanVoiceReview, // '/pantry/scan/voice-review'
                    parentNavigatorKey: _rootKey,
                    builder: (context, state) => VoiceReviewScreen(
                      job: state.extra as ScanJob? ??
                          const ScanJob(id: 'manual', type: ScanType.voice),
                    ),
                  ),
                  GoRoute(
                    path: Routes.scanFailed, // '/pantry/scan/failed'
                    parentNavigatorKey: _rootKey,
                    builder: (context, state) =>
                        ScanFailedScreen(type: state.extra as ScanType?),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            navigatorKey: _suggestionsKey,
            routes: [
              GoRoute(
                path: Routes.suggestions,
                builder: (context, state) => const SuggestionListScreen(),
                routes: [
                  GoRoute(
                    path: Routes.dish, // '/suggestions/dish/:id'
                    parentNavigatorKey: _rootKey,
                    builder: (context, state) => DishDetailScreen(
                      dishId: state.pathParameters['id']!,
                      suggestion: state.extra as DishSuggestion?,
                    ),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            navigatorKey: _shoppingKey,
            routes: [
              GoRoute(
                path: Routes.shopping,
                builder: (context, state) => const ShoppingListScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            navigatorKey: _profileKey,
            routes: [
              GoRoute(
                path: Routes.profile,
                builder: (context, state) => const SettingsHomeScreen(),
              ),
            ],
          ),
        ],
      ),
      GoRoute(
        path: Routes.cookResult,
        parentNavigatorKey: _rootKey,
        builder: (context, state) =>
            CookResultScreen(result: state.extra! as CookResult),
      ),
      GoRoute(
        path: Routes.notifications,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const NotificationCenterScreen(),
      ),
      GoRoute(
        path: Routes.mealPlan,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const MealPlanScreen(),
      ),
      GoRoute(
        path: Routes.reports,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const ReportsScreen(),
      ),
      GoRoute(
        path: Routes.paywall,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const PaywallScreen(),
      ),
      GoRoute(
        path: Routes.settingsProfile,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: Routes.settingsPreferences,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const PreferencesScreen(),
      ),
      GoRoute(
        path: Routes.settingsNotifications,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const NotificationSettingsScreen(),
      ),
      GoRoute(
        path: Routes.settingsPantrySharing,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const PantrySharingScreen(),
      ),
      GoRoute(
        path: Routes.settingsSubscription,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const SubscriptionScreen(),
      ),
      GoRoute(
        path: Routes.settingsAbout,
        parentNavigatorKey: _rootKey,
        builder: (context, state) => const AboutScreen(),
      ),
    ],
  );
}
