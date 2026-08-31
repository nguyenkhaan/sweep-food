// lib/core/widgets/waveform_recorder.dart
// Live mic-amplitude bar visualizer for voice capture (I-06).

import 'dart:collection';

import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_colors.dart';

/// Renders a scrolling row of bars driven by a `0.0`–`1.0` amplitude [stream]
/// (see `AudioRecorderService.amplitude`). When the stream is idle the bars
/// idle at a low baseline so the control still reads as "listening".
class WaveformRecorder extends StatefulWidget {
  const WaveformRecorder({
    required this.stream,
    this.barCount = 32,
    this.color = BrandPalette.green600,
    super.key,
  });

  final Stream<double> stream;
  final int barCount;
  final Color color;

  @override
  State<WaveformRecorder> createState() => _WaveformRecorderState();
}

class _WaveformRecorderState extends State<WaveformRecorder> {
  late final Queue<double> _levels =
      Queue<double>.from(List.filled(widget.barCount, 0.08));

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<double>(
      stream: widget.stream,
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          _levels
            ..addLast(snapshot.data!.clamp(0.04, 1.0))
            ..removeFirst();
        }
        return SizedBox(
          height: 64,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              for (final level in _levels)
                AnimatedContainer(
                  duration: const Duration(milliseconds: 120),
                  width: 4,
                  height: 6 + level * 52,
                  margin: const EdgeInsets.symmetric(horizontal: 2),
                  decoration: BoxDecoration(
                    color: widget.color,
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
}
