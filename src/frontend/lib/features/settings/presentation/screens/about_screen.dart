import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/config/app_constants.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_snackbar.dart';
import 'package:frontend/features/settings/presentation/widgets/settings_group.dart';

/// P-06 Giới thiệu & dữ liệu — data sources + the estimate/health disclaimer.
class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Giới thiệu & dữ liệu')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.lg, Gap.lg, Gap.xxl),
        children: [
          Center(
            child: Column(
              children: [
                Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    color: context.colors.primaryContainer,
                    borderRadius: Radii.brLg,
                  ),
                  child: Icon(
                    Icons.eco_rounded,
                    size: 34,
                    color: context.colors.onPrimaryContainer,
                  ),
                ),
                Gap.gapSm,
                Text(
                  AppConstants.appName,
                  style: context.text.titleMedium
                      ?.copyWith(fontWeight: FontWeight.w700),
                ),
                Text(
                  'Phiên bản 1.0.0 (MVP)',
                  style: context.text.bodySmall?.copyWith(
                    color: context.sweep.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Gap.gapLg,
          const SettingsGroup(
            label: 'Nguồn dữ liệu',
            rows: [
              SettingsRow(
                icon: Icons.restaurant_rounded,
                label: 'Giá trị dinh dưỡng thực phẩm',
                trailing: 'Viện Dinh dưỡng QG',
              ),
              SettingsRow(
                icon: Icons.ac_unit_rounded,
                label: 'Thời gian bảo quản tham khảo',
                trailing: 'FoodKeeper',
              ),
            ],
          ),
          Gap.gapMd,
          Container(
            padding: const EdgeInsets.all(Gap.md),
            decoration: const BoxDecoration(
              color: BrandPalette.brick100,
              borderRadius: Radii.brLg,
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.warning_amber_rounded,
                  size: 18,
                  color: BrandPalette.brick500,
                ),
                Gap.gapSm,
                Expanded(
                  child: Text(
                    'Thông tin dinh dưỡng và thời gian bảo quản chỉ mang tính '
                    'ước tính, không thay thế tư vấn của chuyên gia dinh dưỡng '
                    'hoặc y tế. Luôn kiểm tra màu sắc, mùi và trạng thái thực '
                    'phẩm trước khi sử dụng.',
                    style: context.text.bodySmall?.copyWith(
                      color: BrandPalette.brick500,
                      height: 1.55,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Gap.gapMd,
          SettingsGroup(
            rows: [
              SettingsRow(
                icon: Icons.description_outlined,
                label: 'Điều khoản sử dụng',
                onTap: () => AppSnack.show(context, 'Sẽ mở trong trình duyệt.'),
              ),
              SettingsRow(
                icon: Icons.shield_outlined,
                label: 'Chính sách bảo mật',
                onTap: () => AppSnack.show(context, 'Sẽ mở trong trình duyệt.'),
              ),
              SettingsRow(
                icon: Icons.star_outline_rounded,
                label: 'Đánh giá ứng dụng',
                onTap: () => AppSnack.show(context, 'Cảm ơn bạn!'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
