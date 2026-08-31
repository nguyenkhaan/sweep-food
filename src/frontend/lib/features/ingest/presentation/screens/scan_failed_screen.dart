// lib/features/ingest/presentation/screens/scan_failed_screen.dart
// I-09 Màn hình báo lỗi scan không thành công
// Design: ScanFailed.dc.html

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

/// I-09 — Không đọc được tem nhãn / hóa đơn / giọng nói.
class ScanFailedScreen extends StatelessWidget {
  const ScanFailedScreen({this.type, super.key});

  final ScanType? type;

  String _title(AppL10n l10n) => switch (type) {
    ScanType.receipt => l10n.scanFailReceiptTitle,
    ScanType.voice => l10n.scanFailVoiceTitle,
    _ => l10n.scanFailLabelTitle,
  };

  List<String> _reasons(AppL10n l10n) => switch (type) {
    ScanType.voice => [
      l10n.scanFailVoiceReason1,
      l10n.scanFailVoiceReason2,
      l10n.scanFailVoiceReason3,
    ],
    _ => [
      l10n.scanFailImgReason1,
      l10n.scanFailImgReason2,
      l10n.scanFailImgReason3,
    ],
  };

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final l10n = context.l10n;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.pop(),
          icon: const Icon(Icons.arrow_back_rounded),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.md, Gap.xl, Gap.xl),
          child: Column(
            children: [
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 88,
                      height: 88,
                      decoration: BoxDecoration(
                        color: BrandPalette.brick100,
                        borderRadius: BorderRadius.circular(24),
                      ),
                      child: Icon(
                        type == ScanType.voice
                            ? Icons.mic_off_outlined
                            : Icons.document_scanner_outlined,
                        size: 40,
                        color: BrandPalette.brick500,
                      ),
                    ),
                    const SizedBox(height: Gap.lg),
                    Text(
                      _title(l10n),
                      textAlign: TextAlign.center,
                      style: context.text.titleLarge?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: Gap.md),
                    Column(
                      children: _reasons(l10n)
                          .map(
                            (reason) => Padding(
                              padding: const EdgeInsets.only(bottom: Gap.xs),
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: Gap.md,
                                  vertical: Gap.sm,
                                ),
                                decoration: BoxDecoration(
                                  color: context.colors.surface,
                                  borderRadius: Radii.brMd,
                                  border: Border.all(color: sweep.hairline),
                                ),
                                child: Row(
                                  children: [
                                    Container(
                                      width: 6,
                                      height: 6,
                                      decoration: BoxDecoration(
                                        color: sweep.textTertiary,
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                    const SizedBox(width: Gap.sm),
                                    Expanded(
                                      child: Text(
                                        reason,
                                        style: context.text.bodyMedium
                                            ?.copyWith(
                                              color: sweep.textSecondary,
                                            ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          )
                          .toList(),
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  ElevatedButton.icon(
                    onPressed: () => context.pop(),
                    icon: const Icon(Icons.refresh_rounded),
                    label: Text(
                      type == ScanType.voice
                          ? l10n.scanFailRerecord
                          : l10n.reviewRetake,
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: BrandPalette.green700,
                      foregroundColor: Colors.white,
                      minimumSize: const Size.fromHeight(50),
                      shape: const RoundedRectangleBorder(
                        borderRadius: Radii.brMd,
                      ),
                    ),
                  ),
                  const SizedBox(height: Gap.sm),
                  TextButton(
                    onPressed: () {
                      context.pop();
                      context.push('${Routes.pantry}/${Routes.addIngredient}');
                    },
                    style: TextButton.styleFrom(
                      foregroundColor: sweep.textSecondary,
                      minimumSize: const Size.fromHeight(48),
                    ),
                    child: Text(l10n.chooserManual),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
