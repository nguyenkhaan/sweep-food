import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/widgets/app_fab.dart';
import 'package:frontend/core/widgets/feature_placeholder.dart';
import 'package:frontend/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';

/// H-01 Trang chủ / Dashboard.
/// TODO(M2): greeting + WasteSavedPill + "Cần dùng sớm" + gợi ý nhanh + tổng quan 4 tầng.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('SweepFood')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const FeaturePlaceholder(title: 'Trang chủ', milestone: 'M2'),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () => showAddEntryChooser(context),
              icon: const Icon(Icons.add),
              label: const Text('Thử nghiệm M4: Thêm nguyên liệu (G-03)'),
            ),
          ],
        ),
      ),
      floatingActionButton: AppFab(
        onPressed: () => showAddEntryChooser(context),
        label: 'Thêm nguyên liệu',
      ),
    );
  }
}

