// lib/features/ingest/presentation/screens/voice_capture_screen.dart
// I-06 Nhập liệu bằng giọng nói (Thu âm)
// Design: VoiceCapture.dc.html

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/media/audio_recorder_service.dart';
import 'package:sweepfood/core/media/media_providers.dart';
import 'package:sweepfood/core/permissions/permission_prime_sheet.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/logger.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/waveform_recorder.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/scan_controller.dart';

/// I-06 — Thu âm giọng nói để thêm nguyên liệu.
class VoiceCaptureScreen extends ConsumerStatefulWidget {
  const VoiceCaptureScreen({super.key});

  @override
  ConsumerState<VoiceCaptureScreen> createState() => _VoiceCaptureScreenState();
}

class _VoiceCaptureScreenState extends ConsumerState<VoiceCaptureScreen> {
  late final AudioRecorderService _recorder;
  Timer? _timer;
  int _seconds = 0;
  bool _listening = false;
  bool _capturing = false;
  bool _submitting = false;
  Stream<double> _amplitude = const Stream<double>.empty();

  @override
  void initState() {
    super.initState();
    _recorder = ref.read(audioRecorderServiceProvider);
    WidgetsBinding.instance.addPostFrameCallback((_) => _begin());
  }

  @override
  void dispose() {
    _timer?.cancel();
    if (_capturing) unawaited(_recorder.cancel());
    super.dispose();
  }

  Future<void> _begin() async {
    final granted = await ensureMediaPermission(
      context,
      ref,
      PermissionKind.microphone,
    );
    if (!mounted) return;

    var capturing = false;
    if (granted) capturing = await _recorder.start();
    if (!mounted) return;

    setState(() {
      _listening = capturing;
      _capturing = capturing;
      _amplitude = _recorder.amplitude();
    });
    if (!capturing) {
      log.w('Voice capture did not start granted=$granted');
      return;
    }
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (mounted) setState(() => _seconds++);
    });
  }

  Future<void> _stopAndReview() async {
    if (_submitting) return;
    setState(() => _submitting = true);
    _timer?.cancel();

    String? path;
    if (_capturing) {
      path = await _recorder.stop();
    }

    if (path == null || path.isEmpty) {
      log.w('Voice submission skipped because no audio file was captured');
      if (mounted) {
        context.pushReplacement(
          '${Routes.pantry}/${Routes.scanFailed}',
          extra: ScanType.voice,
        );
      }
      return;
    }

    try {
      final job = await ref
          .read(scanControllerProvider.notifier)
          .scanVoice(audioPath: path);
      if (!mounted) return;
      log.d(
        'Scan result type=voice status=${job.status.name} '
        'items=${job.items.length} hasTranscript=${job.rawText?.isNotEmpty == true}',
      );
      if (job.isFailed || !job.hasItems) {
        context.pushReplacement(
          '${Routes.pantry}/${Routes.scanFailed}',
          extra: ScanType.voice,
        );
        return;
      }
      context.pushReplacement(
        '${Routes.pantry}/${Routes.scanVoiceReview}',
        extra: job,
      );
    } on Object catch (error, stackTrace) {
      log.e('Voice scan flow failed', error: error, stackTrace: stackTrace);
      if (mounted) {
        context.pushReplacement(
          '${Routes.pantry}/${Routes.scanFailed}',
          extra: ScanType.voice,
        );
      }
    }
  }

  String _formatTimer(int total) =>
      '${total ~/ 60}:${(total % 60).toString().padLeft(2, '0')}';

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final l10n = context.l10n;

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: context.colors.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: l10n.voiceCaptureTitle,
              onBack: () => context.pop(),
            ),
            Expanded(
              child: SafeArea(
                top: false,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(
                    Gap.lg,
                    Gap.sm,
                    Gap.lg,
                    Gap.xl,
                  ),
                  child: Column(
                    children: [
                      Text(
                        l10n.voiceCapturePrompt,
                        textAlign: TextAlign.center,
                        style: context.text.titleLarge?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      Gap.gapSm,
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: Gap.md,
                          vertical: Gap.sm + 2,
                        ),
                        decoration: BoxDecoration(
                          color: context.colors.surfaceContainerLowest,
                          borderRadius: Radii.brLg,
                          border: Border.all(color: sweep.hairline),
                        ),
                        child: Text(
                          l10n.voiceCaptureExample,
                          textAlign: TextAlign.center,
                          style: context.text.bodySmall?.copyWith(
                            color: sweep.textSecondary,
                          ),
                        ),
                      ),
                      Expanded(
                        child: Center(
                          child: WaveformRecorder(stream: _amplitude),
                        ),
                      ),
                      Text(
                        _listening ? l10n.voiceListening : l10n.voiceMicOff,
                        textAlign: TextAlign.center,
                        style: context.text.titleSmall?.copyWith(
                          color: _listening
                              ? context.colors.primary
                              : sweep.textTertiary,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _formatTimer(_seconds),
                        style: AppTypography.tabular(
                          context.text.bodyMedium?.copyWith(
                            color: sweep.textTertiary,
                          ),
                        ),
                      ),
                      const SizedBox(height: Gap.xl),
                      Material(
                        color: sweep.ctaWarm,
                        shape: const CircleBorder(),
                        child: InkWell(
                          customBorder: const CircleBorder(),
                          onTap: _submitting
                              ? null
                              : () {
                                  AppHaptics.medium();
                                  _stopAndReview();
                                },
                          child: SizedBox(
                            width: 78,
                            height: 78,
                            child: _submitting
                                ? Padding(
                                    padding: const EdgeInsets.all(24),
                                    child: CircularProgressIndicator(
                                      color: sweep.onCtaWarm,
                                      strokeWidth: 3,
                                    ),
                                  )
                                : Center(
                                    child: Container(
                                      width: 24,
                                      height: 24,
                                      decoration: BoxDecoration(
                                        color: sweep.onCtaWarm,
                                        borderRadius: BorderRadius.circular(5),
                                      ),
                                    ),
                                  ),
                          ),
                        ),
                      ),
                      const SizedBox(height: Gap.sm),
                      Text(
                        l10n.voiceStopReview,
                        style: context.text.labelLarge?.copyWith(
                          fontWeight: FontWeight.w700,
                          color: sweep.textSecondary,
                        ),
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
