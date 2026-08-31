// test/helpers/ingest_fixtures.dart
// Canned ScanJob objects mirroring assets/mock/scan_*.json for ingest tests.
import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/ingest/domain/entities/scan_job.dart';
import 'package:frontend/features/ingest/domain/entities/scan_type.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';

ScanJob labelScanJob() => ScanJob(
      id: 'job_label_001',
      type: ScanType.label,
      fieldCount: 5,
      sourcePath: 'path/to/label.jpg',
      rawText: 'CA CHUA BI 500 g',
      items: [
        ParsedItemDraft(
          name: 'Cà chua bi',
          category: 'Rau củ',
          quantity: 500,
          storageTier: StorageTier.fridge,
          packedDate: DateTime(2026, 9, 3),
          expiryDate: DateTime(2026, 9, 10),
          priceVnd: 18000,
          isExpiryWarn: true,
        ),
      ],
    );

ScanJob receiptScanJob() => ScanJob(
      id: 'job_receipt_001',
      type: ScanType.receipt,
      storeName: 'Bách Hóa Xanh',
      purchaseDate: DateTime(2026, 9, 5),
      items: const [
        ParsedItemDraft(
          name: 'Cà chua bi',
          category: 'Rau củ',
          quantity: 500,
          priceVnd: 18000,
        ),
        ParsedItemDraft(
          name: 'Trứng gà',
          category: 'Trứng & Sữa',
          quantity: 10,
          unit: MeasurementUnit.fruit,
          priceVnd: 32000,
        ),
        ParsedItemDraft(
          name: 'Thịt ba chỉ',
          category: 'Thịt & Hải sản',
          quantity: 300,
          priceVnd: 45000,
          isExpiryWarn: true,
        ),
        ParsedItemDraft(
          name: 'Sữa tươi',
          category: 'Trứng & Sữa',
          quantity: 1,
          unit: MeasurementUnit.liter,
          priceVnd: 36000,
        ),
        ParsedItemDraft(
          name: 'Hành lá',
          category: 'Rau củ',
          quantity: 1,
          unit: MeasurementUnit.bunch,
          priceVnd: 5000,
          isExpiryWarn: true,
        ),
        ParsedItemDraft(
          name: 'Dầu ăn',
          category: 'Gia vị',
          quantity: 1,
          unit: MeasurementUnit.bottle,
          storageTier: StorageTier.pantryShelf,
          priceVnd: 42000,
        ),
      ],
    );

ScanJob voiceScanJob() => const ScanJob(
      id: 'job_voice_001',
      type: ScanType.voice,
      rawText: '2 lạng thịt bò, 1 bó cải bó xôi, 3 quả trứng',
      items: [
        ParsedItemDraft(
          name: 'Thịt bò',
          category: 'Thịt & Hải sản',
          quantity: 200,
        ),
        ParsedItemDraft(
          name: 'Cải bó xôi',
          category: 'Rau củ',
          quantity: 1,
          unit: MeasurementUnit.bunch,
        ),
        ParsedItemDraft(
          name: 'Trứng gà',
          category: 'Trứng & Sữa',
          quantity: 3,
          unit: MeasurementUnit.fruit,
        ),
      ],
    );
