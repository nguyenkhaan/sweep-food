import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';

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

  static const _items = [
    (Icons.home_outlined, Icons.home_rounded, 'Trang chủ'),
    (Icons.kitchen_outlined, Icons.kitchen_rounded, 'Kho'),
    (Icons.auto_awesome_outlined, Icons.auto_awesome_rounded, 'Gợi ý'),
    (Icons.shopping_cart_outlined, Icons.shopping_cart_rounded, 'Mua sắm'),
    (Icons.person_outline_rounded, Icons.person_rounded, 'Cá nhân'),
  ];

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: Theme.of(context).dividerColor)),
        boxShadow: Shadows.e2,
      ),
      child: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: onTap,
        destinations: [
          for (var i = 0; i < _items.length; i++)
            NavigationDestination(
              icon: (i == 0 && notificationBadge)
                  ? Badge(smallSize: 7, child: Icon(_items[i].$1))
                  : Icon(_items[i].$1),
              selectedIcon: Icon(_items[i].$2),
              label: _items[i].$3,
            ),
        ],
      ),
    );
  }
}
