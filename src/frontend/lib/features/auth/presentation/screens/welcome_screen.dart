import 'package:flutter/material.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/widgets/app_text_button.dart';
import 'package:frontend/core/widgets/primary_button.dart';
import 'package:go_router/go_router.dart';

/// A-01 Welcome / value prop — 3 slides on the app's three core values.
class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen> {
  final _controller = PageController();
  int _page = 0;

  static const _slides = [
    (
      icon: Icons.schedule_rounded,
      title: 'Biến nguyên liệu đang có thành bữa ăn',
      body:
          'SweepFood theo dõi hạn dùng và luôn đẩy những món cần dùng sớm lên đầu.',
    ),
    (
      icon: Icons.restaurant_menu_rounded,
      title: 'Gợi ý món hợp tủ bếp của bạn',
      body:
          '3–5 món mỗi lần, chấm điểm theo nguyên liệu sẵn có và đồ sắp hết hạn.',
    ),
    (
      icon: Icons.eco_rounded,
      title: 'Nấu hết đồ, bớt lãng phí',
      body:
          'Xem bạn đã dùng kịp bao nhiêu nguyên liệu trước hạn — tính bằng kg tránh bỏ phí.',
    ),
  ];

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.lg, Gap.xl, Gap.xl),
          child: Column(
            children: [
              Row(
                children: [
                  Icon(Icons.eco_rounded, color: theme.colorScheme.primary),
                  Gap.gapXs,
                  Text(
                    'SweepFood',
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.w700),
                  ),
                ],
              ),
              Expanded(
                child: PageView.builder(
                  controller: _controller,
                  itemCount: _slides.length,
                  onPageChanged: (i) => setState(() => _page = i),
                  itemBuilder: (context, i) {
                    final s = _slides[i];
                    return Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 160,
                          height: 160,
                          decoration: BoxDecoration(
                            color: theme.colorScheme.primaryContainer,
                            borderRadius: Radii.brXl,
                          ),
                          child: Icon(
                            s.icon,
                            size: 72,
                            color: theme.colorScheme.onPrimaryContainer,
                          ),
                        ),
                        Gap.gapXl,
                        Text(
                          s.title,
                          textAlign: TextAlign.center,
                          style: theme.textTheme.headlineSmall
                              ?.copyWith(fontWeight: FontWeight.w700),
                        ),
                        Gap.gapSm,
                        Text(
                          s.body,
                          textAlign: TextAlign.center,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    );
                  },
                ),
              ),
              _Dots(count: _slides.length, active: _page),
              Gap.gapLg,
              PrimaryButton(
                label: 'Bắt đầu',
                onPressed: () => context.push(Routes.register),
              ),
              Gap.gapXs,
              AppTextButton(
                label: 'Đã có tài khoản? Đăng nhập',
                onPressed: () => context.push(Routes.login),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Dots extends StatelessWidget {
  const _Dots({required this.count, required this.active});

  final int count;
  final int active;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        for (var i = 0; i < count; i++)
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            margin: const EdgeInsets.symmetric(horizontal: 3),
            width: i == active ? 20 : 7,
            height: 7,
            decoration: BoxDecoration(
              color: i == active
                  ? scheme.primary
                  : scheme.outlineVariant,
              borderRadius: Radii.brSm,
            ),
          ),
      ],
    );
  }
}
