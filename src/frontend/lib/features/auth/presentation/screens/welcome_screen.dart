import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// A-01 Welcome / value prop — matches Welcome.dc.html exactly:
/// - Brand row at top (logo + "SweepFood")
/// - Large hero art card (.art) with blobs & illustration
/// - Title (.h) + subtitle (.s)
/// - Sliding pill dots (.dots)
/// - Primary + Ghost CTA buttons (.cta)
class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen> {
  final _controller = PageController();
  int _page = 0;

  static const _icons = [
    Icons.schedule_rounded,
    Icons.restaurant_menu_rounded,
    Icons.eco_rounded,
  ];

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final l10n = context.l10n;

    final slides = [
      (
        icon: _icons[0],
        title: l10n.welcomeSlide1Title,
        body: l10n.welcomeSlide1Body,
      ),
      (
        icon: _icons[1],
        title: l10n.welcomeSlide2Title,
        body: l10n.welcomeSlide2Body,
      ),
      (
        icon: _icons[2],
        title: l10n.welcomeSlide3Title,
        body: l10n.welcomeSlide3Body,
      ),
    ];

    // Colors matching Welcome.dc.html & WelcomeDark.dc.html
    final artBg = isDark ? const Color(0xFF17301F) : BrandPalette.green100;
    final blob1Bg = isDark
        ? Colors.white.withValues(alpha: 0.06)
        : Colors.white.withValues(alpha: 0.5);
    final blob2Bg = isDark ? const Color(0xFF245A43) : BrandPalette.green300;
    final iconColor = isDark ? BrandPalette.green400 : BrandPalette.green700;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.md, Gap.xl, Gap.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Top Brand Header
              Row(
                children: [
                  ClipRRect(
                    borderRadius: Radii.brSm,
                    child: Image.asset(
                      'assets/images/sf_icon.png',
                      width: 26,
                      height: 26,
                      fit: BoxFit.contain,
                    ),
                  ),
                  const SizedBox(width: 9),
                  Text(
                    'SweepFood',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      letterSpacing: -0.2,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: Gap.md),

              // Swipeable Area: Art banner + Title + Body
              Expanded(
                child: PageView.builder(
                  controller: _controller,
                  itemCount: slides.length,
                  onPageChanged: (i) => setState(() => _page = i),
                  itemBuilder: (context, i) {
                    final s = slides[i];
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Large Hero Art Container (.art)
                        Expanded(
                          child: Container(
                            decoration: BoxDecoration(
                              color: artBg,
                              borderRadius: BorderRadius.circular(24),
                            ),
                            clipBehavior: Clip.antiAlias,
                            child: Stack(
                              children: [
                                // Blob 1 (top-left)
                                Positioned(
                                  top: 26,
                                  left: 32,
                                  child: Container(
                                    width: 120,
                                    height: 120,
                                    decoration: BoxDecoration(
                                      color: blob1Bg,
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                ),
                                // Blob 2 (bottom-right)
                                Positioned(
                                  bottom: 34,
                                  right: 40,
                                  child: Container(
                                    width: 70,
                                    height: 70,
                                    decoration: BoxDecoration(
                                      color: blob2Bg,
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                ),
                                // Central Illustration / Icon
                                Center(
                                  child: i == 0 || i == 2
                                      ? Image.asset(
                                          'assets/images/sf_icon.png',
                                          width: 130,
                                          height: 130,
                                          fit: BoxFit.contain,
                                        )
                                      : Icon(
                                          s.icon,
                                          size: 110,
                                          color: iconColor,
                                        ),
                                ),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(height: Gap.lg),

                        // Copy Section (.copy: .h + .s)
                        Text(
                          s.title,
                          style: theme.textTheme.headlineSmall?.copyWith(
                            fontSize: 25,
                            fontWeight: FontWeight.w700,
                            letterSpacing: -0.5,
                            height: 1.22,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          s.body,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            fontSize: 14,
                            color: theme.colorScheme.onSurfaceVariant,
                            height: 1.5,
                          ),
                        ),
                      ],
                    );
                  },
                ),
              ),
              const SizedBox(height: Gap.md),

              // Dots indicator (.dots)
              _Dots(count: slides.length, active: _page),
              const SizedBox(height: Gap.lg),

              // CTA buttons (.cta: .btn.pri + .btn.ghost)
              SizedBox(
                height: 50,
                child: FilledButton(
                  onPressed: () => context.push(Routes.register),
                  style: FilledButton.styleFrom(
                    backgroundColor: BrandPalette.green700,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    textStyle: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  child: Text(l10n.welcomeStart),
                ),
              ),
              const SizedBox(height: 10),
              SizedBox(
                height: 50,
                child: TextButton(
                  onPressed: () => context.push(Routes.login),
                  style: TextButton.styleFrom(
                    foregroundColor: theme.colorScheme.onSurfaceVariant,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    textStyle: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  child: Text(l10n.welcomeHaveAccount),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Dots extends StatelessWidget {
  const _Dots({required this.count, required this.active});

  final int count;
  final int active;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final activeColor =
        isDark ? BrandPalette.green600 : BrandPalette.green700;
    final inactiveColor =
        isDark ? const Color(0xFF2E362F) : const Color(0xFFE1E3DE);

    return Row(
      children: [
        for (var i = 0; i < count; i++)
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            margin: const EdgeInsets.only(right: 6),
            width: i == active ? 20 : 7,
            height: 7,
            decoration: BoxDecoration(
              color: i == active ? activeColor : inactiveColor,
              borderRadius: BorderRadius.circular(999),
            ),
          ),
      ],
    );
  }
}
