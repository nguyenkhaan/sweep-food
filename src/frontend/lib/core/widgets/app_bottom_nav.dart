import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Persistent 5-tab botanical bottom navigation bar.
/// Order: Trang chủ · Kho · Gợi ý · Mua sắm · Cá nhân.
class AppBottomNav extends StatelessWidget {
  const AppBottomNav({
    required this.currentIndex,
    required this.onTap,
    this.notificationBadge = false,
    super.key,
  });

  final int currentIndex;
  final ValueChanged<int> onTap;
  final bool notificationBadge;

  static const _icons = [
    AppIcons.home,
    AppIcons.pantry,
    AppIcons.suggestions,
    AppIcons.shopping,
    AppIcons.profile,
  ];

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final labels = [
      l10n.navHome,
      l10n.navPantry,
      l10n.navSuggestions,
      l10n.navShopping,
      l10n.navProfile,
    ];
    final duration = AppMotion.resolve(context, context.motion.fast);

    return DecoratedBox(
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        border: Border(top: BorderSide(color: context.sweep.hairline)),
      ),
      child: NavigationBarTheme(
        data: NavigationBarThemeData(
          height: 66,
          backgroundColor: context.colors.surfaceContainerLowest,
          surfaceTintColor: Colors.transparent,
          indicatorColor: context.colors.primaryContainer,
          indicatorShape: const StadiumBorder(),
          iconTheme: WidgetStateProperty.resolveWith((states) {
            final selected = states.contains(WidgetState.selected);
            return IconThemeData(
              size: 21,
              color: selected
                  ? context.colors.primary
                  : context.sweep.textTertiary,
            );
          }),
          labelTextStyle: WidgetStateProperty.resolveWith((states) {
            final selected = states.contains(WidgetState.selected);
            return context.text.labelSmall?.copyWith(
              letterSpacing: 0,
              fontSize: 11,
              fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
              color: selected
                  ? context.colors.primary
                  : context.sweep.textTertiary,
            );
          }),
        ),
        child: NavigationBar(
          selectedIndex: currentIndex,
          animationDuration: duration,
          onDestinationSelected: (idx) {
            AppHaptics.selection();
            onTap(idx);
          },
          destinations: [
            for (var i = 0; i < _icons.length; i++)
              NavigationDestination(
                icon: (i == 0 && notificationBadge)
                    ? Badge(
                        smallSize: 7,
                        backgroundColor: context.sweep.ctaWarm,
                        child: Icon(_icons[i]),
                      )
                    : Icon(_icons[i]),
                selectedIcon: Icon(_icons[i]),
                label: labels[i],
              ),
          ],
        ),
      ),
    );
  }
}
