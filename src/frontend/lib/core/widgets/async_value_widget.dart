import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/error/error_mapper.dart';
import 'package:frontend/core/error/failure.dart';
import 'package:frontend/core/widgets/error_view.dart';
import 'package:frontend/core/widgets/loading_skeleton.dart';

/// Renders an [AsyncValue]: [data] on success, a skeleton while loading, an
/// [ErrorView] (with retry) on error. Keeps screens free of `.when(...)` noise.
class AsyncValueWidget<T> extends StatelessWidget {
  const AsyncValueWidget({
    required this.value,
    required this.data,
    this.loading,
    this.onRetry,
    this.skeletonCount = 5,
    super.key,
  });

  final AsyncValue<T> value;
  final Widget Function(T data) data;
  final Widget? loading;
  final VoidCallback? onRetry;
  final int skeletonCount;

  @override
  Widget build(BuildContext context) {
    return value.when(
      skipLoadingOnReload: true,
      skipLoadingOnRefresh: true,
      data: data,
      loading: () => loading ?? SkeletonList(count: skeletonCount),
      error: (err, st) {
        final failure = err is Failure ? err : mapError(err, st);
        return ErrorView.fromFailure(failure, onRetry: onRetry);
      },
    );
  }
}
