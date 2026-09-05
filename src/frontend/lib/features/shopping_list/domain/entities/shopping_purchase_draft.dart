import 'package:sweepfood/shared/domain/storage_tier.dart';

/// Collected when checking off a shopping-list item — the backend requires
/// this to create the resulting inventory batch (`purchase` on `PATCH
/// .../items/{item_id}`, forbidden when un-checking). See
/// `docs/api-contract.md` §8.
class ShoppingPurchaseDraft {
  const ShoppingPurchaseDraft({
    required this.storageTier,
    this.expiryDate,
    this.priceVnd,
    this.note,
  });

  final StorageTier storageTier;
  final DateTime? expiryDate;
  final int? priceVnd;
  final String? note;

  Map<String, dynamic> toBody() => {
        'storage_mode': storageTier.backendWire,
        'purchased_at': DateTime.now().toUtc().toIso8601String(),
        if (expiryDate != null)
          'expires_at': expiryDate!.toUtc().toIso8601String(),
        if (priceVnd != null) 'unit_cost': priceVnd,
        if (note != null && note!.trim().isNotEmpty) 'note': note!.trim(),
      };
}
