// lib/features/ingest/presentation/screens/scan_failed_screen.dart
// I-09 Màn hình báo lỗi scan không thành công
// Design: ScanFailed.dc.html

import 'package:flutter/material.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:go_router/go_router.dart';

/// I-09 — Màn hình thông báo lỗi khi không đọc được tem nhãn / hóa đơn.
class ScanFailedScreen extends StatelessWidget {
  const ScanFailedScreen({
    this.title = 'Không đọc được nhãn',
    this.reasons = const [
      'Ảnh bị mờ hoặc chụp nghiêng',
      'Nhãn bị rách hoặc phai mực',
      'Thiếu sáng khi chụp',
    ],
    super.key,
  });

  final String title;
  final List<String> reasons;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;

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
              // ── Center illustration & reasons ──────────────────────────────
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
                      child: const Icon(
                        Icons.document_scanner_outlined,
                        size: 40,
                        color: BrandPalette.brick500,
                      ),
                    ),
                    const SizedBox(height: Gap.lg),
                    Text(
                      title,
                      textAlign: TextAlign.center,
                      style: context.text.titleLarge?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: Gap.md),
                    Column(
                      children: reasons.map((reason) {
                        return Padding(
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
                                    style: context.text.bodyMedium?.copyWith(
                                      color: sweep.textSecondary,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),

              // ── Action buttons ─────────────────────────────────────────────
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  ElevatedButton.icon(
                    onPressed: () => context.pop(),
                    icon: const Icon(Icons.refresh_rounded),
                    label: const Text('Chụp lại'),
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
                    child: const Text('Nhập tay'),
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
