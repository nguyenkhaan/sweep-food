import 'package:flutter/material.dart';

/// Thin [Scaffold] wrapper so screens share one shape (back button, title,
/// actions, optional bottom action bar). Optional — use a plain [Scaffold]
/// where this doesn't fit.
class AppScaffold extends StatelessWidget {
  const AppScaffold({
    required this.body,
    this.title,
    this.titleWidget,
    this.actions,
    this.showBack = true,
    this.bottomBar,
    this.floatingActionButton,
    this.floatingActionButtonLocation,
    super.key,
  });

  final Widget body;
  final String? title;
  final Widget? titleWidget;
  final List<Widget>? actions;
  final bool showBack;

  /// Sticky bar pinned to the bottom (e.g. a primary CTA).
  final Widget? bottomBar;
  final Widget? floatingActionButton;
  final FloatingActionButtonLocation? floatingActionButtonLocation;

  @override
  Widget build(BuildContext context) {
    final hasAppBar = title != null || titleWidget != null || actions != null;
    return Scaffold(
      appBar: hasAppBar
          ? AppBar(
              automaticallyImplyLeading: showBack,
              title: titleWidget ?? (title != null ? Text(title!) : null),
              actions: actions,
            )
          : null,
      body: SafeArea(child: body),
      floatingActionButton: floatingActionButton,
      floatingActionButtonLocation: floatingActionButtonLocation,
      bottomNavigationBar: bottomBar == null
          ? null
          : _BottomBar(child: bottomBar!),
    );
  }
}

class _BottomBar extends StatelessWidget {
  const _BottomBar({required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerLowest,
        border: Border(top: BorderSide(color: Theme.of(context).dividerColor)),
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 12),
          child: child,
        ),
      ),
    );
  }
}
