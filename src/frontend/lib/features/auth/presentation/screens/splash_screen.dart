import 'package:flutter/material.dart';

/// Blank transition while the router restores the persisted session.
///
/// Android already renders the branded launch screen, so this route must not
/// introduce a second logo or loading screen before navigation completes.
class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) => const Scaffold();
}
