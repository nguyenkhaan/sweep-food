import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// App entry point.
/// TODO: move init to bootstrap.dart, mount [SweepFoodApp] with AppRouter + AppTheme.
void main() {
  runApp(const ProviderScope(child: _ScaffoldReady()));
}

class _ScaffoldReady extends StatelessWidget {
  const _ScaffoldReady();

  @override
  Widget build(BuildContext context) => const MaterialApp(
        debugShowCheckedModeBanner: false,
        home: Scaffold(
          body: Center(child: Text('SweepFood — project scaffold ready')),
        ),
      );
}
