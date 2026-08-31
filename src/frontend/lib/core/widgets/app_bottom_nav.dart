import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';

/// The app's 5-tab bottom navigation bar.
/// Order (plan.md §4): Trang chủ · Kho · Gợi ý · Mua sắm · Cá nhân.
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
    (Icons.home_outlined, Icons.home_rounded),
    (Icons.kitchen_outlined, Icons.kitchen_rounded),
    (Icons.auto_awesome_outlined, Icons.auto_awesome_rounded),
    (Icons.shopping_cart_outlined, Icons.shopping_cart_rounded),
    (Icons.person_outline_rounded, Icons.person_rounded),
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
    return DecoratedBox(
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: Theme.of(context).dividerColor)),
        boxShadow: Shadows.e2,
      ),
      child: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: onTap,
        destinations: [
          for (var i = 0; i < _icons.length; i++)
            NavigationDestination(
              icon: (i == 0 && notificationBadge)
                  ? Badge(smallSize: 7, child: Icon(_icons[i].$1))
                  : Icon(_icons[i].$1),
              selectedIcon: Icon(_icons[i].$2),
              label: labels[i],
            ),
        ],
      ),
    );
  }
}
