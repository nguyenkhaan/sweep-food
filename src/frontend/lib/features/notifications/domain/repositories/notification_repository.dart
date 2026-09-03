import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/notifications/domain/entities/app_notification.dart';

abstract interface class NotificationRepository {
  /// `GET /notifications` — newest first (one backend page).
  Future<Result<List<AppNotification>>> list();

  /// `PATCH /notifications/{id}` with `{ status: "READ" }`.
  Future<Result<void>> markRead(String id);

  /// Marks every notification read (client fans out over [markRead]).
  Future<Result<void>> markAllRead(Iterable<String> ids);
}
