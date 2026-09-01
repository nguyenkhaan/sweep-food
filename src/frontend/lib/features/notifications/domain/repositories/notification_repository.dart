import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/notifications/domain/entities/app_notification.dart';

abstract interface class NotificationRepository {
  /// `GET /notifications` — newest first.
  Future<Result<List<AppNotification>>> list();

  /// `POST /notifications/{id}/read`.
  Future<Result<void>> markRead(String id);

  /// Marks every notification read (client fans out over [markRead] in the mock).
  Future<Result<void>> markAllRead(Iterable<String> ids);
}
