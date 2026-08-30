import 'package:flutter/material.dart';
import 'package:frontend/app/router/route_guards.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/shell/app_shell.dart';
import 'package:frontend/features/home/presentation/screens/home_screen.dart';
import 'package:frontend/features/pantry/presentation/screens/add_ingredient_screen.dart';
import 'package:frontend/features/pantry/presentation/screens/pantry_item_detail_screen.dart';
import 'package:frontend/features/pantry/presentation/screens/pantry_screen.dart';
import 'package:frontend/features/settings/presentation/screens/settings_home_screen.dart';
import 'package:frontend/features/shopping_list/presentation/screens/shopping_list_screen.dart';
import 'package:frontend/features/suggestions/presentation/screens/suggestion_list_screen.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'app_router.g.dart';

final _rootKey = GlobalKey<NavigatorState>(debugLabel: 'root');
final _homeKey = GlobalKey<NavigatorState>(debugLabel: 'home');
final _pantryKey = GlobalKey<NavigatorState>(debugLabel: 'pantry');
final _suggestionsKey = GlobalKey<NavigatorState>(debugLabel: 'suggestions');
final _shoppingKey = GlobalKey<NavigatorState>(debugLabel: 'shopping');
final _profileKey = GlobalKey<NavigatorState>(debugLabel: 'profile');

/// The app's [GoRouter], provided via Riverpod so redirects can react to auth
/// state (from M5). Kept alive for the app's lifetime.
@Riverpod(keepAlive: true)
GoRouter appRouter(Ref ref) {
  return GoRouter(
    navigatorKey: _rootKey,
    initialLocation: Routes.initialLocation,
    debugLogDiagnostics: true,
    redirect: appRedirect,
    routes: [
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) =>
            AppShell(navigationShell: navigationShell),
        branches: [
          StatefulShellBranch(
            navigatorKey: _homeKey,
            routes: [
              GoRoute(
                path: Routes.home,
                builder: (context, state) => const HomeScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            navigatorKey: _pantryKey,
            routes: [
              GoRoute(
                path: Routes.pantry,
                builder: (context, state) => const PantryScreen(),
                routes: [
                  GoRoute(
                    path: Routes.addIngredient, // '/pantry/add'
                    parentNavigatorKey: _rootKey,
                    builder: (context, state) =>
                        AddIngredientScreen(editItemId: state.extra as String?),
                  ),
                  GoRoute(
                    path: Routes.pantryItem, // '/pantry/item/:id'
                    parentNavigatorKey: _rootKey,
                    builder: (context, state) => PantryItemDetailScreen(
                      itemId: state.pathParameters['id']!,
                    ),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            navigatorKey: _suggestionsKey,
            routes: [
              GoRoute(
                path: Routes.suggestions,
                builder: (context, state) => const SuggestionListScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            navigatorKey: _shoppingKey,
            routes: [
              GoRoute(
                path: Routes.shopping,
                builder: (context, state) => const ShoppingListScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            navigatorKey: _profileKey,
            routes: [
              GoRoute(
                path: Routes.profile,
                builder: (context, state) => const SettingsHomeScreen(),
              ),
            ],
          ),
        ],
      ),
    ],
  );
}
