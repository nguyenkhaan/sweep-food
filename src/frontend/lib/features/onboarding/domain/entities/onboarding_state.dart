/// The post-signup onboarding flow (A-05, A-06). Two steps; both skippable.
///
/// The design shows a 3-segment progress bar (Splash counts as step 1), so the
/// bars render as `stepNumber` filled out of [totalBars].
enum OnboardingStep {
  dietaryPreference,
  firstPantry;

  /// 1-based position within the visible flow.
  int get stepNumber => index + 2;

  static const totalBars = 3;

  bool get isLast => this == OnboardingStep.firstPantry;
}
