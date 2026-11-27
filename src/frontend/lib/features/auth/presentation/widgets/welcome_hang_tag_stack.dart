import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';

import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Content model for a single hang-tag card on [WelcomeHangTagStack].
@immutable
class HangTagCardData {
  const HangTagCardData({
    required this.tagLabel,
    required this.metric,
    required this.icon,
    required this.title,
    required this.subtitle,
    this.metricIcon = AppIcons.checkCircle,
  });

  final String tagLabel;
  final String metric;
  final IconData icon;
  final String title;
  final String subtitle;
  final IconData metricIcon;
}

/// Interactive pair of kitchen hang-tag cards suspended by threaded cords.
///
/// Interactions (designed to never compete with horizontal `PageView` swipes):
/// - Entry sway: gentle pendulum oscillation when the slide enters view.
/// - Tap back tag: swaps front and back tags along an arc with spring sway.
/// - Tap front tag: nudges the tag into a damped pendulum swing on its cord.
/// - Vertical drag on front tag: pulls the tag downward along its taut cord;
///   releasing snaps back via spring physics (pulling past threshold swaps).
class WelcomeHangTagStack extends StatefulWidget {
  const WelcomeHangTagStack({
    super.key,
    required this.frontData,
    required this.backData,
    this.isActive = true,
  });

  final HangTagCardData frontData;
  final HangTagCardData backData;
  final bool isActive;

  @override
  State<WelcomeHangTagStack> createState() => _WelcomeHangTagStackState();
}

class _WelcomeHangTagStackState extends State<WelcomeHangTagStack>
    with TickerProviderStateMixin {
  static const double _holeLocalY = 16.0;
  static const double _maxPull = 54.0;
  static const double _swapPullThreshold = 42.0;

  late final AnimationController _swapCtrl;
  late final AnimationController _swingCtrl;
  late final AnimationController _backSwingCtrl;
  late final AnimationController _pullCtrl;

  bool _isSwapped = false;
  bool _hasPlayedEntrySway = false;
  double _dragTilt = 0.0;

  static const _pendulumSpring = SpringDescription(
    mass: 1.0,
    stiffness: 95.0,
    damping: 7.2,
  );

  static const _pullReturnSpring = SpringDescription(
    mass: 1.0,
    stiffness: 260.0,
    damping: 16.0,
  );

  @override
  void initState() {
    super.initState();
    _swapCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 420),
    );
    _swingCtrl = AnimationController.unbounded(vsync: this, value: 0.0);
    _backSwingCtrl = AnimationController.unbounded(vsync: this, value: 0.0);
    _pullCtrl = AnimationController.unbounded(vsync: this, value: 0.0);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_hasPlayedEntrySway && widget.isActive) {
      _hasPlayedEntrySway = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted) return;
        _triggerPendulum(_swingCtrl, velocity: 1.45, initialOffset: -0.05);
        _triggerPendulum(_backSwingCtrl, velocity: -0.9, initialOffset: 0.03);
      });
    }
  }

  @override
  void didUpdateWidget(covariant WelcomeHangTagStack oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isActive && !oldWidget.isActive) {
      _triggerPendulum(_swingCtrl, velocity: 1.6, initialOffset: -0.06);
      _triggerPendulum(_backSwingCtrl, velocity: -1.0, initialOffset: 0.04);
    }
  }

  @override
  void dispose() {
    _swapCtrl.dispose();
    _swingCtrl.dispose();
    _backSwingCtrl.dispose();
    _pullCtrl.dispose();
    super.dispose();
  }

  bool get _reduceMotion => MediaQuery.disableAnimationsOf(context);

  void _triggerPendulum(
    AnimationController ctrl, {
    required double velocity,
    double? initialOffset,
  }) {
    if (_reduceMotion) {
      ctrl.value = 0.0;
      return;
    }
    final start = initialOffset ?? ctrl.value.clamp(-0.26, 0.26);
    ctrl.animateWith(SpringSimulation(_pendulumSpring, start, 0.0, velocity));
  }

  void _swapCards() {
    AppHaptics.selection();
    _isSwapped = !_isSwapped;
    if (_reduceMotion) {
      _swapCtrl.value = _isSwapped ? 1.0 : 0.0;
      return;
    }
    final target = _isSwapped ? 1.0 : 0.0;
    _swapCtrl.animateTo(target, curve: Curves.easeInOutCubicEmphasized);
    _triggerPendulum(_swingCtrl, velocity: _isSwapped ? -1.8 : 1.8);
    _triggerPendulum(_backSwingCtrl, velocity: _isSwapped ? 1.2 : -1.2);
  }

  void _handleFrontTapUp(TapUpDetails details, double cardWidth) {
    AppHaptics.light();
    final dxNormalized = ((details.localPosition.dx / cardWidth) - 0.5) * 2;
    final direction = dxNormalized >= 0 ? 1.0 : -1.0;
    _triggerPendulum(_swingCtrl, velocity: direction * 2.1);
    _triggerPendulum(_backSwingCtrl, velocity: -direction * 0.65);
  }

  void _handleVerticalDragStart(DragStartDetails details) {
    _pullCtrl.stop();
    _swingCtrl.stop();
  }

  void _handleVerticalDragUpdate(DragUpdateDetails details) {
    final nextRaw = _pullCtrl.value + details.delta.dy * 0.72;
    // Soft rubber-band resistance past 36dp
    final clamped = nextRaw.clamp(-10.0, _maxPull);
    _pullCtrl.value = clamped;
    setState(() {
      _dragTilt = (details.delta.dx * 0.004 + _dragTilt * 0.85).clamp(
        -0.12,
        0.12,
      );
    });
  }

  void _handleVerticalDragEnd(DragEndDetails details) {
    final velocity = details.primaryVelocity ?? 0.0;
    final currentPull = _pullCtrl.value;
    final shouldSwap = currentPull >= _swapPullThreshold || velocity > 420.0;

    setState(() => _dragTilt = 0.0);

    if (_reduceMotion) {
      _pullCtrl.value = 0.0;
    } else {
      _pullCtrl.animateWith(
        SpringSimulation(
          _pullReturnSpring,
          currentPull,
          0.0,
          (velocity * 0.15).clamp(-300.0, 300.0),
        ),
      );
    }

    if (shouldSwap) {
      AppHaptics.medium();
      _swapCards();
    } else {
      AppHaptics.light();
      _triggerPendulum(
        _swingCtrl,
        velocity: (currentPull >= 0 ? 1.4 : -1.2),
        initialOffset: _dragTilt,
      );
    }
  }

  void _handleVerticalDragCancel() {
    setState(() => _dragTilt = 0.0);
    if (_reduceMotion) {
      _pullCtrl.value = 0.0;
    } else {
      _pullCtrl.animateWith(
        SpringSimulation(_pullReturnSpring, _pullCtrl.value, 0.0, 0.0),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;

    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final height = constraints.maxHeight;
        final cardWidth = (width - Gap.xl * 2).clamp(240.0, 336.0);
        final compact = height < 280;
        final cardHeight = compact ? 132.0 : 148.0;

        final pin = Offset(
          width * 0.5,
          compact ? 12.0 : (height * 0.11).clamp(24.0, 42.0),
        );
        final backRestHole = Offset(
          width * 0.485,
          pin.dy + (compact ? 42.0 : (height * 0.22).clamp(58.0, 82.0)),
        );
        final frontRestHole = Offset(
          width * 0.515,
          backRestHole.dy + (compact ? 54.0 : 64.0),
        );

        const backRestAngle = -3.8 * math.pi / 180;
        const frontRestAngle = 1.8 * math.pi / 180;
        const backRestScale = 0.94;
        const frontRestScale = 1.0;

        return AnimatedBuilder(
          animation: Listenable.merge([
            _swapCtrl,
            _swingCtrl,
            _backSwingCtrl,
            _pullCtrl,
          ]),
          builder: (context, _) {
            final t = _swapCtrl.value;
            // Smooth separation arc peaking at t = 0.5 so tags pass cleanly.
            final arc = math.sin(t * math.pi);
            final pull = _pullCtrl.value;
            final frontSwing = _swingCtrl.value + _dragTilt;
            final backSwing = _backSwingCtrl.value;

            // Card A starts in Front (t = 0) and moves to Back (t = 1).
            final aIsFrontNow = t < 0.5;
            final aPull = aIsFrontNow ? pull : 0.0;
            final aSwing = aIsFrontNow ? frontSwing : backSwing;
            final aHole = Offset(
              _lerp(frontRestHole.dx, backRestHole.dx, t) - arc * 16.0,
              _lerp(frontRestHole.dy, backRestHole.dy, t) + aPull,
            );
            final aAngle =
                _lerp(frontRestAngle, backRestAngle, t) + aSwing - arc * 0.06;
            final aScale = _lerp(frontRestScale, backRestScale, t);

            // Card B starts in Back (t = 0) and moves to Front (t = 1).
            final bIsFrontNow = !aIsFrontNow;
            final bPull = bIsFrontNow ? pull : 0.0;
            final bSwing = bIsFrontNow ? frontSwing : backSwing;
            final bHole = Offset(
              _lerp(backRestHole.dx, frontRestHole.dx, t) + arc * 16.0,
              _lerp(backRestHole.dy, frontRestHole.dy, t) + bPull,
            );
            final bAngle =
                _lerp(backRestAngle, frontRestAngle, t) + bSwing + arc * 0.06;
            final bScale = _lerp(backRestScale, frontRestScale, t);

            final cardASpec = _RenderedTagSpec(
              key: const ValueKey('hang_tag_light'),
              data: widget.frontData,
              isLightCard: true,
              isFrontSlot: aIsFrontNow,
              hole: aHole,
              angle: aAngle,
              scale: aScale,
              pull: aPull,
            );

            final cardBSpec = _RenderedTagSpec(
              key: const ValueKey('hang_tag_emerald'),
              data: widget.backData,
              isLightCard: false,
              isFrontSlot: bIsFrontNow,
              hole: bHole,
              angle: bAngle,
              scale: bScale,
              pull: bPull,
            );

            final backTag = aIsFrontNow ? cardBSpec : cardASpec;
            final frontTag = aIsFrontNow ? cardASpec : cardBSpec;

            return Stack(
              clipBehavior: Clip.none,
              children: [
                // 1. Back cord (from top pin down behind the back tag)
                Positioned.fill(
                  child: IgnorePointer(
                    child: CustomPaint(
                      painter: _CordSegmentPainter(
                        pin: pin,
                        hole: backTag.hole,
                        angle: backTag.angle,
                        pull: backTag.pull,
                        holeLocalY: _holeLocalY * backTag.scale,
                        cordColor: sweep.hangCord.withValues(alpha: 0.72),
                        isFrontLoop: false,
                      ),
                    ),
                  ),
                ),

                // 2. Back tag (tap to swap to front)
                _buildTagLayer(
                  spec: backTag,
                  cardWidth: cardWidth,
                  cardHeight: cardHeight,
                ),

                // 3. Back tag's front threaded cord loop (wraps over top rim into hole)
                Positioned.fill(
                  child: IgnorePointer(
                    child: CustomPaint(
                      painter: _CordSegmentPainter(
                        pin: pin,
                        hole: backTag.hole,
                        angle: backTag.angle,
                        pull: backTag.pull,
                        holeLocalY: _holeLocalY * backTag.scale,
                        cordColor: sweep.hangCord.withValues(alpha: 0.78),
                        isFrontLoop: true,
                      ),
                    ),
                  ),
                ),

                // 4. Front cord (from top pin down behind the front tag)
                Positioned.fill(
                  child: IgnorePointer(
                    child: CustomPaint(
                      painter: _CordSegmentPainter(
                        pin: pin,
                        hole: frontTag.hole,
                        angle: frontTag.angle,
                        pull: frontTag.pull,
                        holeLocalY: _holeLocalY * frontTag.scale,
                        cordColor: sweep.hangCord.withValues(alpha: 0.96),
                        isFrontLoop: false,
                      ),
                    ),
                  ),
                ),

                // 5. Front tag (tap to swing, pull vertically along cord)
                _buildTagLayer(
                  spec: frontTag,
                  cardWidth: cardWidth,
                  cardHeight: cardHeight,
                ),

                // 6. Front tag's front threaded cord loop
                Positioned.fill(
                  child: IgnorePointer(
                    child: CustomPaint(
                      painter: _CordSegmentPainter(
                        pin: pin,
                        hole: frontTag.hole,
                        angle: frontTag.angle,
                        pull: frontTag.pull,
                        holeLocalY: _holeLocalY * frontTag.scale,
                        cordColor: sweep.hangCord,
                        isFrontLoop: true,
                      ),
                    ),
                  ),
                ),

                // 7. Clean minimal mounting pin at the top anchor point (no glow)
                Positioned.fill(
                  child: IgnorePointer(
                    child: CustomPaint(
                      painter: _AnchorPinPainter(
                        pin: pin,
                        ringColor: sweep.hangCord,
                        fillColor: sweep.heroSurfaceElevated,
                      ),
                    ),
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Widget _buildTagLayer({
    required _RenderedTagSpec spec,
    required double cardWidth,
    required double cardHeight,
  }) {
    final holeAlignY = (_holeLocalY / cardHeight) * 2 - 1;
    final pivot = Alignment(0.0, holeAlignY);

    return Positioned(
      key: spec.key,
      left: spec.hole.dx - cardWidth / 2,
      top: spec.hole.dy - _holeLocalY,
      width: cardWidth,
      height: cardHeight,
      child: Transform(
        alignment: pivot,
        transform: Matrix4.identity()
          ..rotateZ(spec.angle)
          ..scaleByDouble(spec.scale, spec.scale, 1.0, 1.0),
        child: Semantics(
          button: true,
          label: '${spec.data.tagLabel}: ${spec.data.title}',
          hint: spec.isFrontSlot
              ? 'Chạm để lắc thẻ hoặc kéo xuống để đổi thẻ'
              : 'Chạm để đưa thẻ này lên phía trước',
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTapUp: spec.isFrontSlot
                ? (d) => _handleFrontTapUp(d, cardWidth)
                : (_) => _swapCards(),
            onVerticalDragStart: spec.isFrontSlot
                ? _handleVerticalDragStart
                : null,
            onVerticalDragUpdate: spec.isFrontSlot
                ? _handleVerticalDragUpdate
                : null,
            onVerticalDragEnd: spec.isFrontSlot ? _handleVerticalDragEnd : null,
            onVerticalDragCancel: spec.isFrontSlot
                ? _handleVerticalDragCancel
                : null,
            child: _HangTagCard(
              data: spec.data,
              isLightCard: spec.isLightCard,
              isFrontSlot: spec.isFrontSlot,
              holeLocalY: _holeLocalY,
            ),
          ),
        ),
      ),
    );
  }

  static double _lerp(double a, double b, double t) => a + (b - a) * t;
}

class _RenderedTagSpec {
  const _RenderedTagSpec({
    required this.key,
    required this.data,
    required this.isLightCard,
    required this.isFrontSlot,
    required this.hole,
    required this.angle,
    required this.scale,
    required this.pull,
  });

  final Key key;
  final HangTagCardData data;
  final bool isLightCard;
  final bool isFrontSlot;
  final Offset hole;
  final double angle;
  final double scale;
  final double pull;
}

class _HangTagCard extends StatelessWidget {
  const _HangTagCard({
    required this.data,
    required this.isLightCard,
    required this.isFrontSlot,
    required this.holeLocalY,
  });

  final HangTagCardData data;
  final bool isLightCard;
  final bool isFrontSlot;
  final double holeLocalY;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final cs = context.colors;

    final bgColor = isLightCard
        ? cs.surfaceContainerLowest
        : sweep.heroSurfaceElevated;
    final borderColor = isLightCard
        ? sweep.hairline.withValues(alpha: 0.7)
        : sweep.onHeroSurface.withValues(alpha: 0.16);
    final eyeletRingColor = isLightCard
        ? sweep.hairline
        : sweep.onHeroSurface.withValues(alpha: 0.28);

    final tagBg = isLightCard
        ? sweep.culinaryAccentBg
        : sweep.onHeroSurface.withValues(alpha: 0.14);
    final tagFg = isLightCard ? sweep.culinaryAccent : sweep.onHeroSurface;
    final metricColor = isLightCard ? cs.primary : sweep.onHeroMuted;
    final iconTileBg = isLightCard
        ? cs.primaryContainer
        : sweep.onHeroSurface.withValues(alpha: 0.12);
    final iconTileFg = isLightCard ? cs.primary : sweep.onHeroSurface;
    final titleColor = isLightCard ? cs.onSurface : sweep.onHeroSurface;
    final subColor = isLightCard ? sweep.textSecondary : sweep.onHeroMuted;

    return Container(
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: Radii.brXl,
        border: Border.all(color: borderColor),
        boxShadow: isFrontSlot ? Shadows.e3 : Shadows.e1,
      ),
      child: Stack(
        children: [
          // Punched hang-tag eyelet centered near the top edge
          Positioned(
            top: holeLocalY - 7.5,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                width: 15,
                height: 15,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: eyeletRingColor, width: 2.0),
                  color: sweep.heroSurface,
                ),
              ),
            ),
          ),

          // Tag content laid out cleanly below the eyelet
          Padding(
            padding: const EdgeInsets.fromLTRB(Gap.md, 28, Gap.md, Gap.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Flexible(
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: Gap.xs + 2,
                          vertical: 3,
                        ),
                        decoration: BoxDecoration(
                          color: tagBg,
                          borderRadius: BorderRadius.circular(Radii.pill),
                        ),
                        child: Text(
                          data.tagLabel,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: context.text.labelSmall?.copyWith(
                            color: tagFg,
                            fontSize: 10,
                            letterSpacing: 0.4,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: Gap.xs),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(data.metricIcon, size: 13.5, color: metricColor),
                        const SizedBox(width: 4),
                        Text(
                          data.metric,
                          maxLines: 1,
                          style: context.text.labelMedium?.copyWith(
                            color: metricColor,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const Spacer(),
                Row(
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: iconTileBg,
                        borderRadius: Radii.brMd,
                      ),
                      child: Icon(data.icon, size: 20, color: iconTileFg),
                    ),
                    const SizedBox(width: Gap.sm),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            data.title,
                            style: context.text.titleSmall?.copyWith(
                              color: titleColor,
                              fontWeight: FontWeight.w700,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 2),
                          Text(
                            data.subtitle,
                            style: context.text.bodySmall?.copyWith(
                              color: subColor,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _CordSegmentPainter extends CustomPainter {
  const _CordSegmentPainter({
    required this.pin,
    required this.hole,
    required this.angle,
    required this.pull,
    required this.holeLocalY,
    required this.cordColor,
    required this.isFrontLoop,
  });

  final Offset pin;
  final Offset hole;
  final double angle;
  final double pull;
  final double holeLocalY;
  final Color cordColor;
  final bool isFrontLoop;

  @override
  void paint(Canvas canvas, Size size) {
    // Smooth continuous twine from top anchor pin straight into the punched hole.
    final delta = pin - hole;
    final dist = delta.distance;
    if (dist < 1.0) return;

    final dirToPin = delta / dist;
    final tension = (pull / 42.0).clamp(0.0, 1.0);
    final mid = Offset.lerp(pin, hole, 0.5)!;
    final slack = (1.0 - tension) * (angle * 16.0);
    final control = Offset(mid.dx - slack, mid.dy);

    // Point where the cord crosses the card's upper rim on its way to the pin.
    final rimDistance = (holeLocalY + 2.5).clamp(10.0, dist * 0.85);
    final rimPoint = hole + dirToPin * rimDistance;

    if (!isFrontLoop) {
      // Main cord from top pin down to just behind the upper rim of the card.
      final path = Path()
        ..moveTo(pin.dx, pin.dy)
        ..quadraticBezierTo(control.dx, control.dy, rimPoint.dx, rimPoint.dy);

      final paint = Paint()
        ..color = cordColor
        ..strokeWidth = 2.0
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round;

      canvas.drawPath(path, paint);
    } else {
      // Front threaded segment emerging from the punched hole and wrapping
      // seamlessly up over the card's top rim to meet the main cord.
      final entryPoint = hole - dirToPin * 1.5;

      final loopPath = Path()
        ..moveTo(entryPoint.dx, entryPoint.dy)
        ..lineTo(rimPoint.dx, rimPoint.dy);

      // Subtle neutral shadow where the cord rests on top of the card's top rim.
      final shadowPaint = Paint()
        ..color = Colors.black.withValues(alpha: 0.14)
        ..strokeWidth = 3.0
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round;
      canvas.drawPath(loopPath.shift(const Offset(0.8, 1.0)), shadowPaint);

      final cordPaint = Paint()
        ..color = cordColor
        ..strokeWidth = 2.1
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round;
      canvas.drawPath(loopPath, cordPaint);
    }
  }

  @override
  bool shouldRepaint(covariant _CordSegmentPainter old) =>
      old.pin != pin ||
      old.hole != hole ||
      old.angle != angle ||
      old.pull != pull ||
      old.cordColor != cordColor ||
      old.isFrontLoop != isFrontLoop;
}

class _AnchorPinPainter extends CustomPainter {
  const _AnchorPinPainter({
    required this.pin,
    required this.ringColor,
    required this.fillColor,
  });

  final Offset pin;
  final Color ringColor;
  final Color fillColor;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawCircle(pin, 5.2, Paint()..color = fillColor);
    canvas.drawCircle(
      pin,
      5.2,
      Paint()
        ..color = ringColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.8,
    );
    canvas.drawCircle(pin, 1.8, Paint()..color = ringColor);
  }

  @override
  bool shouldRepaint(covariant _AnchorPinPainter old) =>
      old.pin != pin ||
      old.ringColor != ringColor ||
      old.fillColor != fillColor;
}
