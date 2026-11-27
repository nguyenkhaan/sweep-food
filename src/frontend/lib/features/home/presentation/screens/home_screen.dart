import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_logo.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/core/widgets/freshness_bar.dart';
import 'package:sweepfood/core/widgets/loading_skeleton.dart';
import 'package:sweepfood/core/widgets/section_header.dart';
import 'package:sweepfood/core/widgets/staggered_reveal.dart';
import 'package:sweepfood/core/widgets/suggestion_card.dart';
import 'package:sweepfood/core/widgets/tactile_card.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/features/home/presentation/controllers/home_controller.dart';
import 'package:sweepfood/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';
import 'package:sweepfood/features/notifications/presentation/controllers/notifications_controller.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/presentation/widgets/suggestion_card_chips.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/expiry_status.dart';

/// H-01 — Home kitchen hub (Concept B · Format 1: Culinary Spotlight Home).
///
/// Compact emerald hero with 3 live KPI pills brings the #1 dish photo card
/// above the fold, followed by a 3-way quick-action dock, compact Pantry
/// Tickets for near-expiry items, and the rest of today's recipe picks.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final homeAsync = ref.watch(homeDashboardProvider);
    final unread = ref.watch(unreadNotificationCountProvider);
    final userName = ref
        .watch(sessionControllerProvider)
        .asData
        ?.value
        ?.user
        .name;
    final cs = context.colors;

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
        backgroundColor: cs.surface,
        body: RefreshIndicator(
          color: context.sweep.ctaWarm,
          onRefresh: () => ref.refresh(homeDashboardProvider.future),
          child: AsyncValueWidget<HomeDashboardData>(
            value: homeAsync,
            onRetry: () => ref.invalidate(homeDashboardProvider),
            loading: _HomeLoadingView(unread: unread, userName: userName),
            data: (data) =>
                _HomeContent(data: data, userName: userName, unread: unread),
          ),
        ),
      ),
    );
  }
}

class _HomeLoadingView extends StatelessWidget {
  const _HomeLoadingView({required this.unread, this.userName});

  final int unread;
  final String? userName;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _HomeTopBarContainer(unread: unread),
        _HomeEmeraldHeroBody(userName: userName),
        const Expanded(child: DelayedSkeleton(child: HomeDashboardSkeleton())),
      ],
    );
  }
}

class _HomeContent extends StatelessWidget {
  const _HomeContent({required this.data, required this.unread, this.userName});

  final HomeDashboardData data;
  final int unread;
  final String? userName;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;

    if (data.isEmpty) {
      return CustomScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        slivers: [
          _buildPinnedBrandSliver(context, unread: unread),
          SliverToBoxAdapter(child: _HomeEmeraldHeroBody(userName: userName)),
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xxl),
            sliver: SliverToBoxAdapter(
              child: EmptyState(
                illustrationAsset: 'assets/illustrations/empty_pantry.svg',
                title: l10n.homeEmptyTitle,
                message: l10n.homeEmptyBody,
                actionLabel: l10n.homeAddFirst,
                onAction: () =>
                    context.push('${Routes.pantry}/${Routes.addIngredient}'),
              ),
            ),
          ),
        ],
      );
    }

    final isVi = Localizations.localeOf(context).languageCode == 'vi';
    final nearCount = data.nearExpiryItems.length;
    final firstSuggestion = data.suggestions.isNotEmpty
        ? data.suggestions.first
        : null;
    final moreSuggestions = data.suggestions.length > 1
        ? data.suggestions.sublist(1)
        : const <DishSuggestion>[];
    final wasteLabel = data.wasteAvoidedKg != null && data.wasteAvoidedKg! > 0
        ? '${data.wasteAvoidedKg!.toStringAsFixed(1).replaceAll('.', ',')} kg'
        : isVi
        ? '${data.wasteSavedCount} món'
        : '${data.wasteSavedCount} saved';

    return CustomScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      slivers: [
        _buildPinnedBrandSliver(context, unread: unread),
        SliverToBoxAdapter(
          child: _HomeEmeraldHeroBody(
            userName: userName,
            pantryCount: data.summary.totalCount,
            nearCount: nearCount,
            suggestionCount: data.suggestionCount,
            onPantryTap: () => context.go(Routes.pantry),
            onSuggestionsTap: () => context.go(Routes.suggestions),
          ),
        ),
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(Gap.lg, 0, Gap.lg, 96),
          sliver: SliverList.list(
            children: [
              // 1. Featured #1 Dish Spotlight right above the fold
              StaggeredReveal(
                index: 0,
                child: Row(
                  children: [
                    Expanded(
                      child: SectionHeader(
                        title: l10n.suggestionsTitle,
                        actionLabel: l10n.seeAll,
                        onAction: () => context.go(Routes.suggestions),
                      ),
                    ),
                  ],
                ),
              ),
              if (data.suggestionCount > 0) ...[
                const SizedBox(height: 4),
                Align(
                  alignment: Alignment.centerLeft,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: Gap.sm,
                      vertical: 3,
                    ),
                    decoration: BoxDecoration(
                      color: cs.primaryContainer,
                      borderRadius: BorderRadius.circular(Radii.pill),
                    ),
                    child: Text(
                      l10n.homeSuggestionCount(data.suggestionCount),
                      style: context.text.labelSmall?.copyWith(
                        letterSpacing: 0,
                        color: cs.onPrimaryContainer,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
              ],
              Gap.gapSm,
              if (firstSuggestion != null) ...[
                StaggeredReveal(
                  index: 1,
                  child: _HomeSuggestionCard(suggestion: firstSuggestion),
                ),
                if (nearCount > 0) ...[
                  const SizedBox(height: Gap.sm),
                  StaggeredReveal(
                    index: 2,
                    child: SizedBox(
                      height: 48,
                      child: FilledButton.icon(
                        style: FilledButton.styleFrom(
                          backgroundColor: sweep.ctaWarm,
                          foregroundColor: sweep.onCtaWarm,
                          elevation: 0,
                          shadowColor: Colors.transparent,
                          shape: const RoundedRectangleBorder(
                            borderRadius: Radii.brLg,
                          ),
                        ),
                        onPressed: () {
                          AppHaptics.light();
                          context.go(Routes.suggestions);
                        },
                        icon: const Icon(AppIcons.cook, size: 18),
                        label: Text(
                          l10n.homeNearExpiryCta(nearCount),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                      ),
                    ),
                  ),
                ],
              ] else
                Container(
                  padding: const EdgeInsets.all(Gap.md),
                  decoration: BoxDecoration(
                    color: sweep.subtleFill,
                    borderRadius: Radii.brLg,
                  ),
                  child: Text(
                    l10n.homeSuggestionsLoadFail,
                    style: context.text.bodyMedium,
                  ),
                ),

              Gap.gapMd,

              // 2. 3-Button Compact Quick Action Dock
              StaggeredReveal(
                index: 3,
                child: IntrinsicHeight(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Expanded(
                        child: _QuickDockButton(
                          icon: AppIcons.scan,
                          iconBg: sweep.culinaryAccentBg,
                          iconFg: sweep.ctaWarm,
                          label: l10n.homeQuickAdd,
                          sublabel: isVi ? 'Quét · Nói' : 'Scan · Voice',
                          onTap: () => showAddEntryChooser(context),
                        ),
                      ),
                      const SizedBox(width: Gap.sm),
                      Expanded(
                        child: _QuickDockButton(
                          icon: AppIcons.calendar,
                          iconBg: cs.primaryContainer,
                          iconFg: cs.primary,
                          label: isVi ? 'Thực đơn' : 'Meal plan',
                          sublabel: isVi ? 'Lên lịch ăn' : 'Schedule',
                          onTap: () => context.push(Routes.mealPlan),
                        ),
                      ),
                      const SizedBox(width: Gap.sm),
                      Expanded(
                        child: _QuickDockButton(
                          icon: AppIcons.leaf,
                          iconBg: sweep.successBg,
                          iconFg: sweep.successFg,
                          label: isVi ? 'Tiết kiệm' : 'Saved',
                          sublabel: wasteLabel,
                          onTap: () => context.push(Routes.reports),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              Gap.gapLg,

              // 3. Near-Expiry Pantry Tickets (exact sibling of Pantry Format 1)
              StaggeredReveal(
                index: 4,
                child: SectionHeader(
                  title: l10n.homeUseSoon,
                  actionLabel: l10n.seeAll,
                  onAction: () => context.go(Routes.pantry),
                ),
              ),
              Gap.gapSm,
              if (data.nearExpiryItems.isEmpty)
                const _AllFreshBanner()
              else
                Column(
                  children: [
                    for (final (idx, item)
                        in data.nearExpiryItems.take(3).indexed) ...[
                      _HomePantryTicket(item: item),
                      if (idx < data.nearExpiryItems.take(3).length - 1)
                        const SizedBox(height: Gap.sm),
                    ],
                  ],
                ),

              // 4. More Today's Suggestions (#2+)
              if (moreSuggestions.isNotEmpty) ...[
                Gap.gapLg,
                SectionHeader(
                  title: isVi ? 'Thêm món hợp tủ bếp' : 'More pantry matches',
                  actionLabel: l10n.seeAll,
                  onAction: () => context.go(Routes.suggestions),
                ),
                Gap.gapSm,
                for (var i = 0; i < moreSuggestions.length; i++)
                  Padding(
                    padding: const EdgeInsets.only(bottom: Gap.md),
                    child: StaggeredReveal(
                      index: i + 5,
                      child: _HomeSuggestionCard(
                        suggestion: moreSuggestions[i],
                      ),
                    ),
                  ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

SliverAppBar _buildPinnedBrandSliver(
  BuildContext context, {
  required int unread,
}) {
  final sweep = context.sweep;
  final l10n = context.l10n;
  return SliverAppBar(
    pinned: true,
    automaticallyImplyLeading: false,
    backgroundColor: sweep.heroSurface,
    surfaceTintColor: Colors.transparent,
    elevation: 0,
    scrolledUnderElevation: 0,
    toolbarHeight: 56,
    titleSpacing: Gap.lg,
    title: Row(
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
      ],
    ),
    actions: [
      Padding(
        padding: const EdgeInsets.only(right: Gap.lg),
        child: _HeroNotificationButton(
          unread: unread,
          tooltip: l10n.notifTitle,
          onPressed: () => context.push(Routes.notifications),
        ),
      ),
    ],
  );
}

class _HomeTopBarContainer extends StatelessWidget {
  const _HomeTopBarContainer({required this.unread});

  final int unread;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final l10n = context.l10n;
    return ColoredBox(
      color: sweep.heroSurface,
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xs),
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
              _HeroNotificationButton(
                unread: unread,
                tooltip: l10n.notifTitle,
                onPressed: () => context.push(Routes.notifications),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Compact deep-emerald Concept B hero body: greeting, headline, optional
/// 3-pill KPI strip, and rising 26dp rounded sheet transition.
class _HomeEmeraldHeroBody extends StatelessWidget {
  const _HomeEmeraldHeroBody({
    this.userName,
    this.pantryCount,
    this.nearCount,
    this.suggestionCount,
    this.onPantryTap,
    this.onSuggestionsTap,
  });

  final String? userName;
  final int? pantryCount;
  final int? nearCount;
  final int? suggestionCount;
  final VoidCallback? onPantryTap;
  final VoidCallback? onSuggestionsTap;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;

    final baseGreeting = _greeting(l10n, DateTime.now().hour);
    final trimmedName = userName?.trim() ?? '';
    final greetingLine = trimmedName.isEmpty
        ? baseGreeting
        : '$baseGreeting, $trimmedName';

    final isVi = Localizations.localeOf(context).languageCode == 'vi';
    final showKpis = pantryCount != null;
    final urgent = (nearCount ?? 0) > 0;
    final sugCount = suggestionCount ?? 0;

    return DecoratedBox(
      decoration: BoxDecoration(color: sweep.heroSurface),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(Gap.lg, 2, Gap.lg, Gap.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  greetingLine,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: context.text.labelLarge?.copyWith(
                    color: sweep.onHeroMuted,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  l10n.homeWhatToEat,
                  style: context.text.headlineMedium?.copyWith(
                    color: sweep.onHeroSurface,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                if (showKpis) ...[
                  const SizedBox(height: Gap.sm + 4),
                  IntrinsicHeight(
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Expanded(
                          child: _HeroKpiPill(
                            value: isVi
                                ? '$pantryCount món'
                                : '$pantryCount ${pantryCount == 1 ? 'item' : 'items'}',
                            label: isVi ? 'Trong kho' : 'In pantry',
                            onTap: onPantryTap,
                          ),
                        ),
                        const SizedBox(width: Gap.xs + 2),
                        Expanded(
                          child: _HeroKpiPill(
                            value: urgent
                                ? (isVi ? '$nearCount cận hạn' : '$nearCount urgent')
                                : (isVi ? 'Tươi tốt' : 'All fresh'),
                            label: l10n.homeUseSoon,
                            highlightWarm: urgent,
                            onTap: onPantryTap,
                          ),
                        ),
                        const SizedBox(width: Gap.xs + 2),
                        Expanded(
                          child: _HeroKpiPill(
                            value: isVi
                                ? '$sugCount gợi ý'
                                : '$sugCount ${sugCount == 1 ? 'dish' : 'dishes'}',
                            label: isVi ? 'Sẵn sàng nấu' : 'Ready to cook',
                            onTap: onSuggestionsTap,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
          Container(
            height: 20,
            decoration: BoxDecoration(
              color: cs.surface,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(26),
              ),
            ),
          ),
        ],
      ),
    );
  }

  static String _greeting(AppL10n l10n, int hour) {
    if (hour < 11) return l10n.greetingMorning;
    if (hour < 14) return l10n.greetingNoon;
    if (hour < 18) return l10n.greetingAfternoon;
    return l10n.greetingEvening;
  }
}

class _HeroKpiPill extends StatelessWidget {
  const _HeroKpiPill({
    required this.value,
    required this.label,
    this.highlightWarm = false,
    this.onTap,
  });

  final String value;
  final String label;
  final bool highlightWarm;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final valueColor = highlightWarm
        ? sweep.culinaryAccentBg
        : sweep.onHeroSurface;

    return Material(
      color: sweep.heroSurfaceElevated,
      shape: RoundedRectangleBorder(
        borderRadius: Radii.brMd,
        side: BorderSide(
          color: highlightWarm
              ? sweep.ctaWarm.withValues(alpha: 0.55)
              : sweep.onHeroSurface.withValues(alpha: 0.14),
        ),
      ),
      child: InkWell(
        borderRadius: Radii.brMd,
        onTap: onTap == null
            ? null
            : () {
                AppHaptics.selection();
                onTap!();
              },
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 9),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                value,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: AppTypography.tabular(
                  context.text.labelLarge?.copyWith(
                    color: valueColor,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              const SizedBox(height: 2),
              Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: context.text.labelSmall?.copyWith(
                  letterSpacing: 0,
                  color: sweep.onHeroMuted,
                  fontSize: 10.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _HeroNotificationButton extends StatelessWidget {
  const _HeroNotificationButton({
    required this.unread,
    required this.tooltip,
    required this.onPressed,
  });

  final int unread;
  final String tooltip;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return Tooltip(
      message: tooltip,
      child: Material(
        color: sweep.heroSurfaceElevated,
        shape: RoundedRectangleBorder(
          borderRadius: Radii.brMd,
          side: BorderSide(color: sweep.onHeroSurface.withValues(alpha: 0.14)),
        ),
        child: InkWell(
          borderRadius: Radii.brMd,
          onTap: () {
            AppHaptics.selection();
            onPressed();
          },
          child: SizedBox(
            width: 44,
            height: 44,
            child: Stack(
              alignment: Alignment.center,
              children: [
                Icon(AppIcons.bell, size: 20, color: sweep.onHeroSurface),
                if (unread > 0)
                  Positioned(
                    top: 10,
                    right: 10,
                    child: Container(
                      width: 9,
                      height: 9,
                      decoration: BoxDecoration(
                        color: sweep.ctaWarm,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: sweep.heroSurfaceElevated,
                          width: 1.5,
                        ),
                      ),
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

class _QuickDockButton extends StatelessWidget {
  const _QuickDockButton({
    required this.icon,
    required this.iconBg,
    required this.iconFg,
    required this.label,
    required this.sublabel,
    required this.onTap,
  });

  final IconData icon;
  final Color iconBg;
  final Color iconFg;
  final String label;
  final String sublabel;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return TactileCard(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 11),
      color: context.colors.surfaceContainerLowest,
      borderColor: sweep.hairline,
      boxShadow: Shadows.e1,
      onTap: () {
        AppHaptics.selection();
        onTap();
      },
      child: Column(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(color: iconBg, borderRadius: Radii.brMd),
            child: Icon(icon, size: 18, color: iconFg),
          ),
          const SizedBox(height: 7),
          Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            textAlign: TextAlign.center,
            style: context.text.labelMedium?.copyWith(
              fontWeight: FontWeight.w700,
              color: context.colors.onSurface,
            ),
          ),
          const SizedBox(height: 1),
          Text(
            sublabel,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            textAlign: TextAlign.center,
            style: context.text.labelSmall?.copyWith(
              letterSpacing: 0,
              color: sweep.textTertiary,
              fontSize: 10.5,
            ),
          ),
        ],
      ),
    );
  }
}

/// Compact Pantry Ticket for the Home "Cần dùng sớm" list — matches
/// PantryItemCard Format 1 (urgency stripe, category icon, freshness bar,
/// dashed divider + countdown stub).
class _HomePantryTicket extends StatelessWidget {
  const _HomePantryTicket({required this.item});

  final PantryItem item;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final level = Expiry.levelFromDays(item.daysUntilExpiry);
    final expColors = sweep.expiry(level);
    final catColors = sweep.categoryForLabel(
      item.category,
      fallbackName: item.name,
    );

    final (stubMain, stubSub) = _countdownStub(item.daysUntilExpiry);

    return Material(
      color: cs.surfaceContainerLowest,
      shape: RoundedRectangleBorder(
        borderRadius: Radii.brXl,
        side: BorderSide(color: sweep.hairline),
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () {
          AppHaptics.selection();
          context.push('${Routes.pantry}/item/${item.id}');
        },
        child: IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(width: 4.5, color: expColors.fg),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(
                    Gap.sm + 4,
                    Gap.sm + 2,
                    Gap.sm + 2,
                    Gap.sm + 2,
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: catColors.bg,
                          borderRadius: Radii.brMd,
                        ),
                        child: Icon(
                          AppIcons.forCategory(
                            item.category,
                            fallbackName: item.name,
                          ),
                          size: 19,
                          color: catColors.fg,
                        ),
                      ),
                      const SizedBox(width: Gap.sm + 2),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              item.name,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: context.text.titleSmall?.copyWith(
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              '${item.quantityLabel} · ${item.storageTier.shortLabel(l10n)}',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: context.text.bodySmall?.copyWith(
                                color: sweep.textSecondary,
                              ),
                            ),
                            const SizedBox(height: 6),
                            FreshnessBar(
                              daysUntilExpiry: item.daysUntilExpiry,
                              referenceDays: item.referenceShelfLifeDays,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              CustomPaint(
                painter: _DashedVerticalPainter(color: sweep.hairline),
                child: const SizedBox(width: 1),
              ),
              Container(
                width: 82,
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 8),
                color: expColors.bg.withValues(alpha: 0.45),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      stubMain,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.center,
                      style: AppTypography.tabular(
                        context.text.labelLarge?.copyWith(
                          color: expColors.fg,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      stubSub,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.center,
                      style: context.text.labelSmall?.copyWith(
                        letterSpacing: 0,
                        color: expColors.fg.withValues(alpha: 0.85),
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  static (String, String) _countdownStub(int? days) {
    if (days == null) return ('—', 'Chưa rõ');
    if (days < 0) return ('Quá hạn', '${days.abs()} ngày');
    if (days == 0) return ('Hôm nay', 'Dùng ngay');
    return ('$days ngày', 'Còn lại');
  }
}

class _DashedVerticalPainter extends CustomPainter {
  const _DashedVerticalPainter({required this.color});

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 1.2;
    const dash = 4.0;
    const gap = 3.0;
    var y = 6.0;
    while (y < size.height - 6) {
      canvas.drawLine(
        Offset(0, y),
        Offset(0, (y + dash).clamp(0, size.height - 6)),
        paint,
      );
      y += dash + gap;
    }
  }

  @override
  bool shouldRepaint(covariant _DashedVerticalPainter old) =>
      old.color != color;
}

class _AllFreshBanner extends StatelessWidget {
  const _AllFreshBanner();

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    return Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: sweep.successBg,
        borderRadius: Radii.brXl,
        border: Border.all(color: sweep.successFg.withValues(alpha: 0.2)),
      ),
      child: Row(
        children: [
          ExcludeSemantics(
            child: SvgPicture.asset(
              'assets/illustrations/home_all_fresh.svg',
              width: 54,
              height: 54,
            ),
          ),
          const SizedBox(width: Gap.sm + 2),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.homeAllFreshTitle,
                  style: context.text.titleSmall?.copyWith(
                    color: sweep.successFg,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Text(
                  l10n.homeNoNearExpiry,
                  style: context.text.bodySmall?.copyWith(
                    color: sweep.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _HomeSuggestionCard extends StatelessWidget {
  const _HomeSuggestionCard({required this.suggestion});

  final DishSuggestion suggestion;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return SuggestionCard(
      title: suggestion.dish.name,
      score: suggestion.score,
      rank: suggestion.rank,
      meta: suggestion.dish.shortMeta(l10n),
      chips: suggestion.cardChips(l10n),
      fitReasons: suggestion.fitReasons.take(3).toList(),
      imageUrl: suggestion.dish.imageUrl,
      heroTag: 'dish-${suggestion.id}',
      onTap: () => context.push(
        '${Routes.suggestions}/dish/${suggestion.id}',
        extra: suggestion,
      ),
    );
  }
}
