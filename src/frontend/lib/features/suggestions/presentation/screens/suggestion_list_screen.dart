import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/widgets/feature_placeholder.dart';

/// S-01 Gợi ý món.
/// TODO(M3): 3–5 SuggestionCard with score + badges, filters (bữa / thời gian / dinh dưỡng).
class SuggestionListScreen extends ConsumerWidget {
  const SuggestionListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Gợi ý cho bạn')),
      body: const FeaturePlaceholder(title: 'Gợi ý', milestone: 'M3'),
    );
  }
}
