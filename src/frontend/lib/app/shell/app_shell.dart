import 'package:flutter/material.dart';
import 'package:frontend/core/widgets/app_bottom_nav.dart';
import 'package:go_router/go_router.dart';

/// The persistent bottom-navigation frame hosting the 5 tab branches.
/// Tab order (plan.md §4): Trang chủ · Kho · Gợi ý · Mua sắm · Cá nhân.
class AppShell extends StatelessWidget {
  const AppShell({required this.navigationShell, super.key});

  final StatefulNavigationShell navigationShell;

  void _onTap(int index) {
    // Tapping the active tab again pops it to its root.
    navigationShell.goBranch(
      index,
      initialLocation: index == navigationShell.currentIndex,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: AppBottomNav(
        currentIndex: navigationShell.currentIndex,
        onTap: _onTap,
      ),
    );
  }
}
