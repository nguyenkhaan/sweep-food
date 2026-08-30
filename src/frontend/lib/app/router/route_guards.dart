import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';

/// Redirect logic for [appRouter].
///
/// **M0–M4: dev-bypass** — always returns `null` (no redirect) so screens can be
/// built without an auth flow.
///
/// **M5:** replace the body with real logic:
///   - no session + not on an auth route  → [Routes.welcome]
///   - has session + on an auth route     → [Routes.home]
///   - has session + onboarding not done  → [Routes.onboardingDiet]
///   - handle FCM deep links from `state.uri`.
String? appRedirect(BuildContext context, GoRouterState state) {
  return null;
}
