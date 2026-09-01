// lib/features/ingest/presentation/screens/add_entry_chooser_sheet.dart
// G-03 — Sheet chọn phương thức nhập nguyên liệu
// Design: AddEntryChooser.dc.html

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Mở sheet này thay vì navigate — dùng [showAddEntryChooser].
Future<void> showAddEntryChooser(BuildContext context) {
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    useSafeArea: true,
    backgroundColor: Colors.transparent,
    builder: (_) => const AddEntryChooserSheet(),
  );
}

/// G-03 — Bottom sheet hiển thị 4 cách nhập nguyên liệu.
///
/// Layout: 2×2 grid. Ô "Quét tem nhãn" dùng màu primary (green-700),
/// các ô còn lại dùng nền surface với border hairline.
class AddEntryChooserSheet extends StatelessWidget {
  const AddEntryChooserSheet({super.key});

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;
    final l10n = context.l10n;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: Radii.brSheet,
        boxShadow: Shadows.e3,
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.sm, Gap.lg, Gap.xl),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // ── Grab handle ─────────────────────────────────────
                Center(
                  child: Container(
                    width: 38,
                    height: 4,
                    decoration: BoxDecoration(
                      color: sweep.hairline,
                      borderRadius: Radii.brSheet,
                    ),
                  ),
                ),
                Gap.gapMd,

                // ── Tiêu đề ─────────────────────────────────────────
                Text(
                  l10n.pantryAddIngredient,
                  style: context.text.titleLarge?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Gap.gapMd,

                // ── 2×2 lưới (row + IntrinsicHeight — co giãn theo cỡ chữ,
                //    không overflow như childAspectRatio cố định) ────────
                IntrinsicHeight(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Expanded(
                        child: _OptionCard(
                          icon: const _CameraIcon(),
                          title: l10n.chooserScanLabel,
                          subtitle: l10n.chooserScanLabelSub,
                          isPrimary: true,
                          onTap: () {
                            context.pop(); // đóng sheet
                            context.push(
                              '${Routes.pantry}/${Routes.scanCamera}?mode=label',
                            );
                          },
                        ),
                      ),
                      const SizedBox(width: Gap.sm),
                      Expanded(
                        child: _OptionCard(
                          icon: const _ReceiptIcon(),
                          title: l10n.chooserScanReceipt,
                          subtitle: l10n.chooserScanReceiptSub,
                          onTap: () {
                            context.pop();
                            context.push(
                              '${Routes.pantry}/${Routes.scanCamera}?mode=receipt',
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: Gap.sm),
                IntrinsicHeight(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Expanded(
                        child: _OptionCard(
                          icon: const _MicIcon(),
                          title: l10n.chooserVoice,
                          subtitle: l10n.chooserVoiceSub,
                          onTap: () {
                            context.pop();
                            context.push(
                              '${Routes.pantry}/${Routes.scanVoiceCapture}',
                            );
                          },
                        ),
                      ),
                      const SizedBox(width: Gap.sm),
                      Expanded(
                        child: _OptionCard(
                          icon: const _KeyboardIcon(),
                          title: l10n.chooserManual,
                          subtitle: l10n.chooserManualSub,
                          onTap: () {
                            context.pop();
                            context.push(
                              '${Routes.pantry}/${Routes.addIngredient}',
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Option Card
// ─────────────────────────────────────────────────────────────────────────────

class _OptionCard extends StatelessWidget {
  const _OptionCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.isPrimary = false,
  });

  final Widget icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final bool isPrimary;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;

    final bgColor = isPrimary ? BrandPalette.green700 : cs.surface;
    final borderColor = isPrimary ? BrandPalette.green700 : sweep.hairline;
    final iconBg = isPrimary
        ? Colors.white.withValues(alpha: 0.16)
        : BrandPalette.green100;
    final iconFg = isPrimary ? Colors.white : BrandPalette.green700;
    final titleColor = isPrimary ? Colors.white : cs.onSurface;
    final subtitleColor = isPrimary
        ? BrandPalette.green100
        : sweep.textTertiary;

    return Material(
      color: bgColor,
      borderRadius: Radii.brLg,
      child: InkWell(
        onTap: onTap,
        borderRadius: Radii.brLg,
        child: Container(
          constraints: const BoxConstraints(minHeight: 116),
          decoration: BoxDecoration(
            border: Border.all(color: borderColor),
            borderRadius: Radii.brLg,
          ),
          padding: const EdgeInsets.all(Gap.md - 1),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Icon badge
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: iconBg,
                  borderRadius: Radii.brSm,
                ),
                child: Center(
                  child: IconTheme(
                    data: IconThemeData(color: iconFg, size: 19),
                    child: icon,
                  ),
                ),
              ),
              const SizedBox(height: Gap.xs),
              // Title + subtitle (nhóm dưới cùng)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    title,
                    style: context.text.labelLarge?.copyWith(
                      color: titleColor,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    subtitle,
                    style: context.text.labelSmall?.copyWith(
                      color: subtitleColor,
                      height: 1.35,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
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

// ─────────────────────────────────────────────────────────────────────────────
// Icon widgets (SVG-matched với design canvas)
// ─────────────────────────────────────────────────────────────────────────────

class _CameraIcon extends StatelessWidget {
  const _CameraIcon();
  @override
  Widget build(BuildContext context) {
    return const Icon(Icons.camera_alt_outlined);
  }
}

class _ReceiptIcon extends StatelessWidget {
  const _ReceiptIcon();
  @override
  Widget build(BuildContext context) {
    return const Icon(Icons.receipt_long_outlined);
  }
}

class _MicIcon extends StatelessWidget {
  const _MicIcon();
  @override
  Widget build(BuildContext context) {
    return const Icon(Icons.mic_outlined);
  }
}

class _KeyboardIcon extends StatelessWidget {
  const _KeyboardIcon();
  @override
  Widget build(BuildContext context) {
    return const Icon(Icons.keyboard_outlined);
  }
}
