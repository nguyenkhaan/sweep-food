import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/entitlements/entitlements.dart';
import 'package:frontend/core/entitlements/entitlements_provider.dart';

/// Shows [child] when [feature] is allowed, otherwise [locked] (default: nothing).
///
/// MVP: `entitlementsProvider` is all-unlocked, so this always renders [child].
/// When gating is real, pass a paywall teaser as [locked].
class Gated extends ConsumerWidget {
  const Gated({
    required this.feature,
    required this.child,
    this.locked = const SizedBox.shrink(),
    super.key,
  });

  final Feature feature;
  final Widget child;
  final Widget locked;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ref.watch(featureAllowedProvider(feature)) ? child : locked;
  }
}
