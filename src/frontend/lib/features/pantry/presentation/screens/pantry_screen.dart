import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/widgets/feature_placeholder.dart';

/// K-01 Kho thực phẩm.
/// TODO(M1): 4-tier segmented list, sort by priority, search, PantryItemCard rows.
class PantryScreen extends ConsumerWidget {
  const PantryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Kho thực phẩm')),
      body: const FeaturePlaceholder(title: 'Kho', milestone: 'M1'),
    );
  }
}
