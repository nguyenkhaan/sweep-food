import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/analytics/analytics_service.dart';
import 'package:sweepfood/core/analytics/noop_analytics_service.dart';

part 'analytics_provider.g.dart';

/// The app-wide [AnalyticsService]. MVP wires [NoopAnalyticsService]; M6 can
/// override this with a Firebase-backed impl in `bootstrap()`.
@Riverpod(keepAlive: true)
AnalyticsService analytics(Ref ref) => const NoopAnalyticsService();
