import 'package:sweepfood/core/analytics/analytics_service.dart';
import 'package:sweepfood/core/utils/logger.dart' as app_log;

/// The only [AnalyticsService] wired in the MVP: it just logs. Swap for a
/// Firebase-backed impl in M6 without touching call sites.
class NoopAnalyticsService implements AnalyticsService {
  const NoopAnalyticsService();

  @override
  void log(String name, [Map<String, Object?> params = const {}]) {
    app_log.log.d('📊 $name${params.isEmpty ? '' : ' $params'}');
  }

  @override
  void setUserProperty(String name, String? value) {
    app_log.log.d('📊 user.$name = $value');
  }
}
