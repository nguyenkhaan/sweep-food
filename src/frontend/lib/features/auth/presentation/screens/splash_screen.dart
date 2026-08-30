import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/config/app_constants.dart';

/// G-01 Splash. Purely visual: [appRedirect] routes on the moment
/// `sessionControllerProvider` resolves (token check + `/auth/me`).
class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      backgroundColor: scheme.primary,
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                color: scheme.onPrimary.withValues(alpha: 0.12),
                borderRadius: Radii.brXl,
              ),
              child: Icon(
                Icons.eco_rounded,
                size: 52,
                color: scheme.onPrimary,
              ),
            ),
            Gap.gapLg,
            Text(
              AppConstants.appName,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: scheme.onPrimary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
