// lib/features/ingest/presentation/screens/voice_capture_screen.dart
// I-06 Nhập liệu bằng giọng nói (Thu âm)
// Design: VoiceCapture.dc.html

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/media/audio_recorder_service.dart';
import 'package:frontend/core/media/media_providers.dart';
import 'package:frontend/core/permissions/permission_prime_sheet.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/waveform_recorder.dart';
import 'package:frontend/features/ingest/presentation/controllers/scan_controller.dart';
import 'package:go_router/go_router.dart';

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
    final granted =
        await ensureMediaPermission(context, ref, PermissionKind.microphone);
    if (!mounted) return;

    var capturing = false;
    if (granted) capturing = await _recorder.start();
    if (!mounted) return;

    setState(() {
      _listening = granted;
      _capturing = capturing;
      _amplitude = _recorder.amplitude();
    });
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

    try {
      final job = await ref
          .read(scanControllerProvider.notifier)
          .scanVoice(audioPath: path);
      if (!mounted) return;
      if (job.isFailed || !job.hasItems) {
        context.pushReplacement('${Routes.pantry}/${Routes.scanFailed}');
        return;
      }
      context.pushReplacement(
        '${Routes.pantry}/${Routes.scanVoiceReview}',
        extra: job,
      );
    } on Object {
      if (mounted) {
        context.pushReplacement('${Routes.pantry}/${Routes.scanFailed}');
      }
    }
  }

  String _formatTimer(int total) =>
      '${total ~/ 60}:${(total % 60).toString().padLeft(2, '0')}';

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
              Expanded(
                child: Center(
                  child: WaveformRecorder(stream: _amplitude),
                ),
              ),
              Text(
                _listening
                    ? 'Đang nghe…'
                    : 'Chưa bật được micro — cứ đọc rồi kiểm tra',
                textAlign: TextAlign.center,
                style: context.text.titleSmall?.copyWith(
                  color: _listening
                      ? BrandPalette.green700
                      : sweep.textTertiary,
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
              const SizedBox(height: Gap.xl),
              GestureDetector(
                onTap: _submitting ? null : _stopAndReview,
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
                  child: _submitting
                      ? const Padding(
                          padding: EdgeInsets.all(22),
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 3,
                          ),
                        )
                      : const Icon(
                          Icons.stop_rounded,
                          size: 36,
                          color: Colors.white,
                        ),
                ),
              ),
              const SizedBox(height: Gap.sm),
              Text(
                'Dừng & Kiểm tra',
                style: context.text.labelLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: sweep.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
