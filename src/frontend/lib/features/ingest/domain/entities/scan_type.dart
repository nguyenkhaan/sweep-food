import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';

/// The three multimodal ingestion channels (M4). `wire` is the API/mock token.
enum ScanType {
  label('label'),
  receipt('receipt'),
  voice('voice');

  const ScanType(this.wire);

  final String wire;

  /// `POST` endpoint that accepts this channel's media.
  String get endpoint => switch (this) {
        ScanType.label => ApiPaths.extractionOcrLabel,
        ScanType.receipt => ApiPaths.extractionOcrInvoice,
        ScanType.voice => ApiPaths.extractionAsr,
      };

  /// Which [PantrySource] a saved item from this channel carries.
  PantrySource get pantrySource => switch (this) {
        ScanType.label => PantrySource.labelScan,
        ScanType.receipt => PantrySource.receiptScan,
        ScanType.voice => PantrySource.voice,
      };

  static ScanType fromWire(String? value) => ScanType.values.firstWhere(
        (t) => t.wire == value,
        orElse: () => ScanType.label,
      );
}

/// Lifecycle of a [ScanJob] as reported by the extraction backend.
enum ScanStatus {
  pending('pending'),
  completed('completed'),
  failed('failed');

  const ScanStatus(this.wire);

  final String wire;

  static ScanStatus fromWire(String? value) {
    final upper = value?.toUpperCase();
    if (upper == 'SUCCEEDED' || upper == 'PARTIAL' || upper == 'COMPLETED') {
      return ScanStatus.completed;
    }
    if (upper == 'FAILED') {
      return ScanStatus.failed;
    }
    if (upper == 'PENDING') {
      return ScanStatus.pending;
    }
    return ScanStatus.values.firstWhere(
      (s) => s.wire == value,
      orElse: () => ScanStatus.completed,
    );
  }
}
