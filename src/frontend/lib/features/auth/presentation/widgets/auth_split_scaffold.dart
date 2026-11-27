import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_logo.dart';

/// Shared Concept B split-hero layout for Auth screens (Login, Register,
/// Forgot Password, OTP, Reset Password).
///
/// Solid deep-emerald header (no ambient glow, bare brand logo) paired with a
/// clean rising rounded sheet that holds the scrollable form.
class AuthSplitScaffold extends StatelessWidget {
  const AuthSplitScaffold({
    required this.title,
    required this.subtitle,
    required this.child,
    this.showBack = true,
    this.onBack,
    super.key,
  });

  final String title;
  final String subtitle;
  final Widget child;
  final bool showBack;
  final VoidCallback? onBack;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final cs = context.colors;

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
        systemNavigationBarColor: cs.surfaceContainerLowest,
        systemNavigationBarIconBrightness:
            Theme.of(context).brightness == Brightness.dark
            ? Brightness.light
            : Brightness.dark,
      ),
      child: Scaffold(
        backgroundColor: sweep.heroSurface,
        resizeToAvoidBottomInset: true,
        body: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            SafeArea(
              bottom: false,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(
                  Gap.lg,
                  Gap.sm,
                  Gap.lg,
                  Gap.lg,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        if (showBack)
                          _HeroBackButton(
                            onPressed:
                                onBack ??
                                () {
                                  if (context.canPop()) {
                                    context.pop();
                                  }
                                },
                          )
                        else
                          const SizedBox(height: 40),
                        const AppLogo(size: 30),
                      ],
                    ),
                    Gap.gapMd,
                    Text(
                      title,
                      style: context.text.headlineMedium?.copyWith(
                        color: sweep.onHeroSurface,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      subtitle,
                      style: context.text.bodyMedium?.copyWith(
                        color: sweep.onHeroMuted,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Expanded(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: cs.surfaceContainerLowest,
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(30),
                  ),
                ),
                child: ClipRRect(
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(30),
                  ),
                  child: SafeArea(
                    top: false,
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.fromLTRB(
                        Gap.xl,
                        Gap.xl,
                        Gap.xl,
                        Gap.xl,
                      ),
                      keyboardDismissBehavior:
                          ScrollViewKeyboardDismissBehavior.onDrag,
                      child: child,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HeroBackButton extends StatelessWidget {
  const _HeroBackButton({required this.onPressed});

  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return Semantics(
      button: true,
      label: MaterialLocalizations.of(context).backButtonTooltip,
      child: Material(
        color: sweep.heroSurfaceElevated,
        borderRadius: Radii.brMd,
        child: InkWell(
          onTap: onPressed,
          borderRadius: Radii.brMd,
          child: SizedBox(
            width: 44,
            height: 44,
            child: Icon(
              AppIcons.arrowLeft,
              size: 20,
              color: sweep.onHeroSurface,
            ),
          ),
        ),
      ),
    );
  }
}

/// Primary warm culinary button used across the Concept B Auth flow.
/// Flat, crisp elevation — no glow shadow.
class AuthPrimaryButton extends StatelessWidget {
  const AuthPrimaryButton({
    required this.label,
    required this.onPressed,
    this.loading = false,
    this.trailingIcon,
    super.key,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool loading;
  final IconData? trailingIcon;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: FilledButton(
        style: FilledButton.styleFrom(
          backgroundColor: sweep.ctaWarm,
          foregroundColor: sweep.onCtaWarm,
          elevation: 0,
          shape: const RoundedRectangleBorder(borderRadius: Radii.brLg),
          textStyle: context.text.labelLarge?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
        onPressed: loading ? null : onPressed,
        child: loading
            ? SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2.2,
                  color: sweep.onCtaWarm,
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(label),
                  if (trailingIcon != null) ...[
                    const SizedBox(width: Gap.xs),
                    Icon(trailingIcon, size: 18),
                  ],
                ],
              ),
      ),
    );
  }
}
