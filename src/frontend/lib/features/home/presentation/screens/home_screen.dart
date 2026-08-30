import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/widgets/feature_placeholder.dart';

/// H-01 Trang chủ / Dashboard.
/// TODO(M2): greeting + WasteSavedPill + "Cần dùng sớm" + gợi ý nhanh + tổng quan 4 tầng.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('SweepFood')),
      body: const FeaturePlaceholder(title: 'Trang chủ', milestone: 'M2'),
    );
  }
}
