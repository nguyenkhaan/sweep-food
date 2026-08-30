import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/async_value_widget.dart';
import 'package:frontend/core/widgets/empty_state.dart';
import 'package:frontend/core/widgets/pantry_item_card.dart';
import 'package:frontend/core/widgets/section_header.dart';
import 'package:frontend/core/widgets/suggestion_card.dart';
import 'package:frontend/core/widgets/waste_saved_pill.dart';
import 'package:frontend/features/home/presentation/controllers/home_controller.dart';
import 'package:frontend/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';
import 'package:frontend/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:frontend/features/suggestions/presentation/widgets/suggestion_card_chips.dart';
import 'package:go_router/go_router.dart';

/// H-01 Trang chủ / Dashboard.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final homeAsync = ref.watch(homeDashboardProvider);

    return Scaffold(
      appBar: AppBar(
        titleSpacing: Gap.lg,
        title: Row(
          children: [
            const Icon(Icons.eco_rounded, color: BrandPalette.green700, size: 24),
            const SizedBox(width: Gap.xs),
            Text(
              'SweepFood',
              style: context.text.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
                color: context.colors.onSurface,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Stack(
              clipBehavior: Clip.none,
              children: [
                const Icon(Icons.notifications_outlined),
                Positioned(
                  top: 2,
                  right: 2,
                  child: Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: BrandPalette.warnCritical,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),
              ],
            ),
            // Notification Center is M5 — no route yet; stub the tap until then.
            onPressed: () => context.showSnack(
              'Trung tâm thông báo sẽ có trong bản cập nhật tới.',
            ),
          ),
          const SizedBox(width: Gap.xs),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.refresh(homeDashboardProvider.future),
        child: AsyncValueWidget<HomeDashboardData>(
          value: homeAsync,
          onRetry: () => ref.invalidate(homeDashboardProvider),
          data: (data) => _HomeContent(data: data),
        ),
      ),
    );
  }
}

class _HomeContent extends StatelessWidget {
  const _HomeContent({required this.data});

  final HomeDashboardData data;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;

    // Empty pantry → greeting + a single "add your first ingredient" CTA
    // (spec M2: "trỏ mock vào fixture kho rỗng để xem empty state").
    if (data.isEmpty) {
      return ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xxl),
        children: [
          const _GreetingHeader(),
          const SizedBox(height: 56),
          EmptyState(
            title: 'Kho của bạn đang trống',
            message:
                'Thêm vài nguyên liệu để nhận gợi ý món và nhắc hạn sử dụng.',
            icon: Icons.kitchen_outlined,
            actionLabel: 'Thêm nguyên liệu đầu tiên',
            onAction: () =>
                context.push('${Routes.pantry}/${Routes.addIngredient}'),
          ),
        ],
      );
    }

    return ListView(
      padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xxl * 2),
      children: [
        // ── Greeting ──────────────────────────────────────────────────────────
        const _GreetingHeader(),
        Gap.gapMd,

        // ── Waste Saved Pill ──────────────────────────────────────────────────
        WasteSavedPill(
          count: data.wasteSavedCount,
          wasteAvoidedKg: data.wasteAvoidedKg,
        ),
        Gap.gapMd,

        // ── Quick Navigation 2x2 Grid ─────────────────────────────────────────
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: Gap.sm,
          crossAxisSpacing: Gap.sm,
          childAspectRatio: 1.4,
          children: [
            _DashboardTile(
              icon: Icons.kitchen_outlined,
              title: 'Kho thực phẩm',
              subtitle: '${data.summary.totalCount} nguyên liệu',
              bgColor: context.colors.surfaceContainerLowest,
              iconBgColor: BrandPalette.green100,
              iconFgColor: BrandPalette.green700,
              onTap: () => context.go(Routes.pantry),
            ),
            _DashboardTile(
              icon: Icons.local_fire_department_outlined,
              title: 'Cần dùng sớm',
              subtitle: '${data.nearExpiryItems.length} nguyên liệu',
              bgColor: BrandPalette.brick100,
              iconBgColor: context.colors.surface,
              iconFgColor: BrandPalette.brick500,
              textColor: BrandPalette.brick500,
              onTap: () => context.go(Routes.pantry),
            ),
            _DashboardTile(
              icon: Icons.auto_awesome_outlined,
              title: 'Gợi ý món',
              subtitle: data.suggestionCount > 0
                  ? '${data.suggestionCount} món phù hợp'
                  : 'Món hợp tủ bếp',
              bgColor: BrandPalette.green700,
              iconBgColor: Colors.white.withValues(alpha: 0.16),
              iconFgColor: Colors.white,
              textColor: Colors.white,
              subtitleColor: BrandPalette.green300,
              onTap: () => context.go(Routes.suggestions),
            ),
            _DashboardTile(
              icon: Icons.qr_code_scanner_rounded,
              title: 'Thêm nhanh',
              subtitle: 'Tem · Hóa đơn · Giọng nói',
              bgColor: BrandPalette.green100,
              iconBgColor: context.colors.surface,
              iconFgColor: BrandPalette.green700,
              textColor: BrandPalette.green800,
              subtitleColor: BrandPalette.green800.withValues(alpha: 0.75),
              onTap: () => showAddEntryChooser(context),
            ),
          ],
        ),
        Gap.gapLg,

        // ── Section: Cần dùng sớm ──────────────────────────────────────────────
        SectionHeader(
          title: 'Cần dùng sớm',
          actionLabel: 'Xem tất cả',
          onAction: () => context.go(Routes.pantry),
        ),
        Gap.gapSm,
        if (data.nearExpiryItems.isEmpty)
          Container(
            padding: const EdgeInsets.all(Gap.md),
            decoration: BoxDecoration(
              color: sweep.subtleFill,
              borderRadius: Radii.brLg,
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.check_circle_outline_rounded,
                  color: BrandPalette.green700,
                  size: 20,
                ),
                const SizedBox(width: Gap.sm),
                Expanded(
                  child: Text(
                    'Không có nguyên liệu nào cận hạn. Tủ bếp của bạn rất tươi tốt!',
                    style: context.text.bodyMedium?.copyWith(
                      color: sweep.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
          )
        else
          SizedBox(
            height: 80,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: data.nearExpiryItems.length,
              separatorBuilder: (_, __) => const SizedBox(width: Gap.sm),
              itemBuilder: (ctx, idx) {
                final item = data.nearExpiryItems[idx];
                return SizedBox(
                  width: 260,
                  child: PantryItemCard(
                    name: item.name,
                    subtitle: '${item.quantityLabel} · ${item.storageTier.label}',
                    daysUntilExpiry: item.daysUntilExpiry,
                    tier: item.storageTier,
                    onTap: () => context.push('${Routes.pantry}/item/${item.id}'),
                  ),
                );
              },
            ),
          ),
        Gap.gapLg,

        // ── Section: Gợi ý cho bạn ───────────────────────────────────────────
        SectionHeader(
          title: 'Gợi ý cho bạn',
          actionLabel: 'Xem tất cả',
          onAction: () => context.go(Routes.suggestions),
        ),
        Gap.gapSm,
        if (data.suggestions.isEmpty)
          Text(
            'Chưa tải được gợi ý. Kéo xuống để làm mới.',
            style: context.text.bodyMedium?.copyWith(
              color: sweep.textSecondary,
            ),
          ),
        for (var i = 0; i < data.suggestions.length; i++) ...[
          if (i > 0) Gap.gapSm,
          _HomeSuggestionCard(suggestion: data.suggestions[i]),
        ],
      ],
    );
  }
}

/// Time-aware greeting shown at the top of Home (both the empty and full state).
class _GreetingHeader extends StatelessWidget {
  const _GreetingHeader();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          _greeting(DateTime.now().hour),
          style: context.text.bodyMedium?.copyWith(
            color: context.sweep.textSecondary,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          'Hôm nay ăn gì?',
          style: context.text.headlineMedium?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }

  static String _greeting(int hour) {
    if (hour < 11) return 'Chào buổi sáng';
    if (hour < 14) return 'Chào buổi trưa';
    if (hour < 18) return 'Chào buổi chiều';
    return 'Chào buổi tối';
  }
}

/// A tappable Home suggestion card → D-01 dish detail (carrying the suggestion
/// so the score badge/chips render without a second fetch).
class _HomeSuggestionCard extends StatelessWidget {
  const _HomeSuggestionCard({required this.suggestion});

  final DishSuggestion suggestion;

  @override
  Widget build(BuildContext context) {
    return SuggestionCard(
      title: suggestion.dish.name,
      score: suggestion.score,
      meta: suggestion.dish.shortMeta,
      chips: suggestion.cardChips,
      onTap: () => context.push(
        '${Routes.suggestions}/dish/${suggestion.id}',
        extra: suggestion,
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Dashboard Tile Component
// ─────────────────────────────────────────────────────────────────────────────

class _DashboardTile extends StatelessWidget {
  const _DashboardTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.bgColor,
    required this.iconBgColor,
    required this.iconFgColor,
    required this.onTap,
    this.textColor,
    this.subtitleColor,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final Color bgColor;
  final Color iconBgColor;
  final Color iconFgColor;
  final Color? textColor;
  final Color? subtitleColor;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final defaultSubColor =
        textColor != null ? textColor!.withValues(alpha: 0.75) : context.sweep.textTertiary;

    return Material(
      color: bgColor,
      borderRadius: Radii.brLg,
      child: InkWell(
        onTap: onTap,
        borderRadius: Radii.brLg,
        child: Container(
          padding: const EdgeInsets.all(Gap.md - 2),
          decoration: BoxDecoration(
            borderRadius: Radii.brLg,
            border: Border.all(
              color: bgColor == context.colors.surfaceContainerLowest
                  ? context.sweep.hairline
                  : Colors.transparent,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                width: 34,
                height: 34,
                decoration: BoxDecoration(
                  color: iconBgColor,
                  borderRadius: Radii.brSm,
                ),
                child: Icon(icon, size: 19, color: iconFgColor),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: context.text.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: textColor ?? context.colors.onSurface,
                    ),
                  ),
                  const SizedBox(height: 1),
                  Text(
                    subtitle,
                    style: context.text.labelSmall?.copyWith(
                      color: subtitleColor ?? defaultSubColor,
                      fontSize: 11,
                    ),
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
