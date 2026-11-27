// lib/features/ingest/presentation/screens/scan_failed_screen.dart
// I-09 Màn hình báo lỗi scan không thành công (Concept B · Format 1)

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
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
    final cs = context.colors;
    final l10n = context.l10n;

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: _title(l10n),
              onBack: () => context.pop(),
            ),
            Expanded(
              child: SafeArea(
                top: false,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(
                    Gap.xl,
                    Gap.md,
                    Gap.xl,
                    Gap.xl,
                  ),
                  child: Column(
                    children: [
                      Expanded(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            ExcludeSemantics(
                              child: SvgPicture.asset(
                                'assets/illustrations/scan_failed.svg',
                                width: 156,
                                height: 122,
                              ),
                            ),
                            const SizedBox(height: Gap.lg),
                            Container(
                              decoration: BoxDecoration(
                                color: cs.surfaceContainerLowest,
                                borderRadius: Radii.brXl,
                                border: Border.all(color: sweep.hairline),
                                boxShadow: Shadows.e1,
                              ),
                              child: Column(
                                children: [
                                  for (final (i, reason) in _reasons(
                                    l10n,
                                  ).indexed) ...[
                                    Padding(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: Gap.md,
                                        vertical: Gap.sm + 4,
                                      ),
                                      child: Row(
                                        children: [
                                          Container(
                                            width: 6,
                                            height: 6,
                                            decoration: BoxDecoration(
                                              color: sweep.ctaWarm,
                                              shape: BoxShape.circle,
                                            ),
                                          ),
                                          const SizedBox(width: Gap.sm + 2),
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
                                    if (i < _reasons(l10n).length - 1)
                                      Divider(height: 1, color: sweep.hairline),
                                  ],
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          FilledButton.icon(
                            onPressed: () => context.pop(),
                            icon: const Icon(AppIcons.refresh, size: 18),
                            label: Text(
                              type == ScanType.voice
                                  ? l10n.scanFailRerecord
                                  : l10n.reviewRetake,
                            ),
                            style: FilledButton.styleFrom(
                              backgroundColor: sweep.ctaWarm,
                              foregroundColor: sweep.onCtaWarm,
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
                              context.push(
                                '${Routes.pantry}/${Routes.addIngredient}',
                              );
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
            ),
          ],
        ),
      ),
    );
  }
}
