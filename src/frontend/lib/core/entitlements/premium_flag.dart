/// Master switch for the Premium gating layer.
///
/// **MVP = `false`**: every feature is unlocked, no 40-ingredient / 10-scan
/// limits, no Paywall blocking. The Paywall screen still exists as an
/// interest-capture page. Flip to `true` (and back `entitlementsProvider` with a
/// real `/subscription` fetch) when commercial gating goes live.
const bool kPremiumEnabled = bool.fromEnvironment('PREMIUM_ENABLED');
