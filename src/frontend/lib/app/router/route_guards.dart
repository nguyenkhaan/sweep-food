import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/features/onboarding/presentation/controllers/onboarding_controller.dart';

/// Routes reachable while signed out.
const _authRoutes = {
  Routes.welcome,
  Routes.login,
  Routes.register,
  Routes.verifyOtp,
  Routes.forgotPassword,
  Routes.resetPassword,
};

const _onboardingRoutes = {Routes.onboardingDiet, Routes.onboardingPantry};

/// Redirect logic for [appRouter]. Reads (never watches) the session + onboarding
/// providers; the router's `refreshListenable` re-runs this whenever either
/// changes.
///
/// | state                         | allowed              | else →            |
/// |-------------------------------|----------------------|-------------------|
/// | session still restoring       | `/splash`            | `/splash`         |
/// | signed out                    | auth routes          | `/welcome`        |
/// | signed in, onboarding pending | onboarding routes    | `/onboarding/diet`|
/// | signed in, onboarded          | everything else      | `/home`           |
String? appRedirect(Ref ref, BuildContext context, GoRouterState state) {
  final session = ref.read(sessionControllerProvider);
  final loc = state.matchedLocation;
  final atSplash = loc == Routes.splash;

  // Cold start: still reading the persisted token / calling /auth/me.
  if (session.isLoading && !session.hasValue) {
    return atSplash ? null : Routes.splash;
  }

  // Resolved (data, or an unexpected error we treat as signed-out).
  final signedIn = session.asData?.value != null;

  if (!signedIn) {
    return _authRoutes.contains(loc) ? null : Routes.welcome;
  }

  if (!ref.read(onboardingControllerProvider)) {
    return _onboardingRoutes.contains(loc) ? null : Routes.onboardingDiet;
  }

  if (atSplash || _authRoutes.contains(loc) || _onboardingRoutes.contains(loc)) {
    return Routes.home;
  }
  return null;
}

/// Bridges the Riverpod providers the guard depends on to a [Listenable] that
/// [GoRouter.refreshListenable] understands.
class AuthRouterRefresh extends ChangeNotifier {
  AuthRouterRefresh(Ref ref) {
    ref
      ..listen(sessionControllerProvider, (_, __) => notifyListeners())
      ..listen(onboardingControllerProvider, (_, __) => notifyListeners());
  }
}
