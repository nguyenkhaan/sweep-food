import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/widgets/feature_placeholder.dart';

/// B-01 Danh sách mua sắm.
/// TODO(M5): generated from meal plan, grouped by category, hide-in-stock toggle, check off.
class ShoppingListScreen extends ConsumerWidget {
  const ShoppingListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Danh sách mua sắm')),
      body: const FeaturePlaceholder(title: 'Mua sắm', milestone: 'M5'),
    );
  }
}
