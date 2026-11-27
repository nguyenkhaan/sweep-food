import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';

import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_logo.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_split_scaffold.dart';
import 'package:sweepfood/features/auth/presentation/widgets/welcome_hang_tag_stack.dart';

/// Welcome / Value-proposition onboarding screen (Concept B · Culinary Split Hero).
///
/// Top 56% deep forest emerald hero with interactive threaded hang-tag cards;
/// bottom 44% rising crisp white/dark surface sheet with clear Vietnamese
/// hierarchy and flat warm culinary CTA.
class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen> {
  final _controller = PageController();
  int _page = 0;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final cs = context.colors;
    final sweep = context.sweep;

    final slides = [
      _WelcomeSlideData(
        badge: 'QUẢN LÝ HẠN DÙNG',
        title: l10n.welcomeSlide1Title,
        body: l10n.welcomeSlide1Body,
        frontCard: const HangTagCardData(
          tagLabel: 'NHẮC SỚM',
          metric: '3 giây',
          icon: AppIcons.scan,
          title: 'Quét tem cân và hóa đơn',
          subtitle: 'Tự nhận diện tên món và hạn sử dụng',
        ),
        backCard: const HangTagCardData(
          tagLabel: 'TỦ BẾP CỦA BẠN',
          metric: 'Còn 2 ngày',
          metricIcon: AppIcons.clock,
          icon: AppIcons.pantry,
          title: 'Cà chua bi · Sữa tươi',
          subtitle: 'Đẩy nguyên liệu sắp hết hạn lên đầu',
        ),
      ),
      _WelcomeSlideData(
        badge: 'GỢI Ý NẤU ĂN',
        title: l10n.welcomeSlide2Title,
        body: l10n.welcomeSlide2Body,
        frontCard: const HangTagCardData(
          tagLabel: 'GỢI Ý #1',
          metric: '100 điểm',
          icon: AppIcons.cook,
          title: 'Canh cà chua thịt băm',
          subtitle: 'Đủ nguyên liệu · Nấu xong trong 25 phút',
        ),
        backCard: const HangTagCardData(
          tagLabel: 'NGUYÊN LIỆU SẴN CÓ',
          metric: '3/3 món',
          metricIcon: AppIcons.checkCircle,
          icon: AppIcons.clock,
          title: 'Thịt heo · Cải ngọt · Cà chua',
          subtitle: 'Ưu tiên dùng đồ sắp hết hạn trước',
        ),
      ),
      _WelcomeSlideData(
        badge: 'CHỐNG LÃNG PHÍ',
        title: l10n.welcomeSlide3Title,
        body: l10n.welcomeSlide3Body,
        frontCard: const HangTagCardData(
          tagLabel: 'TIẾT KIỆM',
          metric: '4,2 kg',
          icon: AppIcons.leaf,
          title: 'Thực phẩm đã dùng kịp hạn',
          subtitle: 'Giảm đồ bỏ phí và tiết kiệm chi tiêu',
        ),
        backCard: const HangTagCardData(
          tagLabel: 'THÁNG NÀY',
          metric: 'Đúng nhu cầu',
          metricIcon: AppIcons.checkCircle,
          icon: AppIcons.shopping,
          title: 'Chỉ mua đúng thứ còn thiếu',
          subtitle: 'Tự đối chiếu tủ bếp trước khi đi chợ',
        ),
      ),
    ];

    final current = slides[_page];

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
        systemNavigationBarColor: cs.surfaceContainerLowest,
        systemNavigationBarIconBrightness:
            Theme.of(context).brightness == Brightness.dark
            ? Brightness.light
            : Brightness.dark,
      ),
      child: Scaffold(
        backgroundColor: sweep.heroSurface,
        body: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Top Deep Forest Emerald Hero ───────────────────────────────
            Expanded(
              flex: 56,
              child: SafeArea(
                bottom: false,
                child: Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(
                        Gap.lg,
                        Gap.md,
                        Gap.lg,
                        0,
                      ),
                      child: Row(
                        children: [
                          const AppLogo(size: 30),
                          const SizedBox(width: Gap.xs + 2),
                          Expanded(
                            child: Text(
                              'SweepFood',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: context.text.titleMedium?.copyWith(
                                color: sweep.onHeroSurface,
                                fontWeight: FontWeight.w800,
                                letterSpacing: -0.3,
                              ),
                            ),
                          ),
                          const SizedBox(width: Gap.sm),
                          Flexible(
                            child: AnimatedSwitcher(
                              duration: AppMotion.resolve(
                                context,
                                context.motion.fast,
                              ),
                              child: Container(
                                key: ValueKey(current.badge),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: Gap.sm + 2,
                                  vertical: 5,
                                ),
                                decoration: BoxDecoration(
                                  color: sweep.ctaWarm,
                                  borderRadius: BorderRadius.circular(
                                    Radii.pill,
                                  ),
                                ),
                                child: Text(
                                  current.badge,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: context.text.labelSmall?.copyWith(
                                    color: sweep.onCtaWarm,
                                    fontSize: 10,
                                    letterSpacing: 0.4,
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Expanded(
                      child: PageView.builder(
                        controller: _controller,
                        itemCount: slides.length,
                        onPageChanged: (i) {
                          AppHaptics.selection();
                          setState(() => _page = i);
                        },
                        itemBuilder: (context, i) => WelcomeHangTagStack(
                          frontData: slides[i].frontCard,
                          backData: slides[i].backCard,
                          isActive: _page == i,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // ── Bottom Rising Rounded Sheet ────────────────────────────────
            DecoratedBox(
              decoration: BoxDecoration(
                color: cs.surfaceContainerLowest,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(30),
                ),
                boxShadow: Shadows.e3,
              ),
              child: SafeArea(
                top: false,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(
                    Gap.xl,
                    Gap.lg,
                    Gap.xl,
                    Gap.lg,
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _Dots(
                        count: slides.length,
                        active: _page,
                        onTap: (i) => _controller.animateToPage(
                          i,
                          duration: AppMotion.resolve(
                            context,
                            context.motion.medium,
                          ),
                          curve: AppMotion.resolveCurve(
                            context,
                            context.motion.enterCurve,
                          ),
                        ),
                      ),
                      Gap.gapMd,
                      AnimatedSwitcher(
                        duration: AppMotion.resolve(
                          context,
                          context.motion.fast,
                        ),
                        child: Column(
                          key: ValueKey(_page),
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              current.title,
                              style: context.text.headlineMedium,
                            ),
                            const SizedBox(height: Gap.xs + 2),
                            Text(
                              current.body,
                              style: context.text.bodyMedium?.copyWith(
                                color: sweep.textSecondary,
                                height: 1.5,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Gap.gapLg,
                      Row(
                        children: [
                          Expanded(
                            flex: 42,
                            child: SizedBox(
                              height: 52,
                              child: OutlinedButton(
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: cs.onSurface,
                                  side: BorderSide(color: sweep.hairline),
                                  shape: const RoundedRectangleBorder(
                                    borderRadius: Radii.brLg,
                                  ),
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: Gap.sm,
                                  ),
                                ),
                                onPressed: () {
                                  AppHaptics.selection();
                                  context.push(Routes.login);
                                },
                                child: Text(
                                  l10n.authSignIn,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: Gap.sm),
                          Expanded(
                            flex: 58,
                            child: AuthPrimaryButton(
                              label: l10n.welcomeStart,
                              trailingIcon: AppIcons.arrowRight,
                              onPressed: () {
                                AppHaptics.light();
                                context.push(Routes.register);
                              },
                            ),
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

class _WelcomeSlideData {
  const _WelcomeSlideData({
    required this.badge,
    required this.title,
    required this.body,
    required this.frontCard,
    required this.backCard,
  });

  final String badge;
  final String title;
  final String body;
  final HangTagCardData frontCard;
  final HangTagCardData backCard;
}

class _Dots extends StatelessWidget {
  const _Dots({required this.count, required this.active, required this.onTap});

  final int count;
  final int active;
  final ValueChanged<int> onTap;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return Row(
      children: [
        for (var i = 0; i < count; i++)
          GestureDetector(
            onTap: () => onTap(i),
            behavior: HitTestBehavior.opaque,
            child: Padding(
              padding: const EdgeInsets.only(right: 6, top: 4, bottom: 4),
              child: AnimatedContainer(
                duration: AppMotion.resolve(context, context.motion.fast),
                width: i == active ? 24 : 7,
                height: 7,
                decoration: BoxDecoration(
                  color: i == active ? sweep.ctaWarm : sweep.hairline,
                  borderRadius: BorderRadius.circular(Radii.pill),
                ),
              ),
            ),
          ),
      ],
    );
  }
}
