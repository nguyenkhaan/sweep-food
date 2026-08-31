// lib/features/ingest/presentation/screens/voice_capture_screen.dart
// I-06 Nhập liệu bằng giọng nói (Thu âm)
// Design: VoiceCapture.dc.html

import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:go_router/go_router.dart';

/// I-06 — Màn hình thu âm giọng nói để thêm nguyên liệu.
class VoiceCaptureScreen extends ConsumerStatefulWidget {
  const VoiceCaptureScreen({super.key});

  @override
  ConsumerState<VoiceCaptureScreen> createState() => _VoiceCaptureScreenState();
}

class _VoiceCaptureScreenState extends ConsumerState<VoiceCaptureScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _animController;
  Timer? _timer;
  int _seconds = 7;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..repeat(reverse: true);

    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (mounted) {
        setState(() => _seconds++);
      }
    });
  }

  @override
  void dispose() {
    _animController.dispose();
    _timer?.cancel();
    super.dispose();
  }

  void _stopAndReview() {
    _timer?.cancel();
    context.push('${Routes.pantry}/${Routes.scanVoiceReview}');
  }

  String _formatTimer(int totalSeconds) {
    final m = totalSeconds ~/ 60;
    final s = totalSeconds % 60;
    return '$m:${s.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.pop(),
          icon: const Icon(Icons.close_rounded),
        ),
        title: const Text('Nói để thêm'),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
          child: Column(
            children: [
              // ── Hint Header ───────────────────────────────────────────────
              Text(
                'Đọc tên nguyên liệu và số lượng',
                textAlign: TextAlign.center,
                style: context.text.titleLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              Gap.gapSm,
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: Gap.md,
                  vertical: Gap.sm,
                ),
                decoration: BoxDecoration(
                  color: sweep.subtleFill,
                  borderRadius: Radii.brMd,
                ),
                child: Text(
                  'VD: “2 lạng thịt bò, 1 bó cải bó xôi, 3 quả trứng”',
                  textAlign: TextAlign.center,
                  style: context.text.bodySmall?.copyWith(
                    color: sweep.textTertiary,
                  ),
                ),
              ),

              // ── Animated Waveform Visualizer ──────────────────────────────
              Expanded(
                child: Center(
                  child: AnimatedBuilder(
                    animation: _animController,
                    builder: (context, _) {
                      return Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: List.generate(14, (i) {
                          final waveFactor = math.sin((i / 14 * math.pi * 2) + (_animController.value * math.pi));
                          final height = (20 + (waveFactor * 24)).abs().clamp(10.0, 54.0);
                          return Container(
                            width: 5,
                            height: height,
                            margin: const EdgeInsets.symmetric(horizontal: 2.5),
                            decoration: BoxDecoration(
                              color: BrandPalette.green600,
                              borderRadius: BorderRadius.circular(999),
                            ),
                          );
                        }),
                      );
                    },
                  ),
                ),
              ),

              // ── Status & Live partial text ────────────────────────────────
              Text(
                'Đang nghe…',
                style: context.text.titleSmall?.copyWith(
                  color: BrandPalette.green700,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                _formatTimer(_seconds),
                style: context.text.bodyMedium?.copyWith(
                  color: sweep.textTertiary,
                ),
              ),
              const SizedBox(height: Gap.md),
              Text(
                '…1 bó cải bó xôi',
                style: context.text.bodyMedium?.copyWith(
                  color: sweep.textSecondary,
                  fontStyle: FontStyle.italic,
                ),
              ),
              const SizedBox(height: Gap.xl),

              // ── Mic & Stop Button ─────────────────────────────────────────
              GestureDetector(
                onTap: _stopAndReview,
                child: Container(
                  width: 78,
                  height: 78,
                  decoration: BoxDecoration(
                    color: BrandPalette.warnCritical,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: BrandPalette.warnCritical.withValues(alpha: 0.25),
                        blurRadius: 0,
                        spreadRadius: 8,
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.stop_rounded,
                    size: 36,
                    color: Colors.white,
                  ),
                ),
              ),
              const SizedBox(height: Gap.sm),
              GestureDetector(
                onTap: _stopAndReview,
                child: Text(
                  'Dừng & Kiểm tra',
                  style: context.text.labelLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: sweep.textSecondary,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
