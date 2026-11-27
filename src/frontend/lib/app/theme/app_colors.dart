import 'package:flutter/material.dart';

/// Tier-1 brand & botanical primitives, plus Tier-2 semantic [SweepColors].
///
/// Widgets read semantic tokens via `context.sweep` / `SweepColors.of(context)`
/// and `context.colors` — never raw `Color(0x...)` literals.
abstract final class BrandPalette {
  // Primary — deep culinary forest emerald (Concept B)
  static const green900 = Color(0xFF063B2D);
  static const green800 = Color(0xFF064E3B); // hero deep emerald
  static const green700 = Color(0xFF0B6E4F); // primary (light)
  static const green600 = Color(0xFF15805B);
  static const green500 = Color(0xFF2EA378);
  static const green400 = Color(0xFF52C497); // primary (dark)
  static const green300 = Color(0xFF8EE0BE);
  static const green200 = Color(0xFFB7E8CD);
  static const green100 = Color(0xFFE6F6EE);

  // Culinary warm tomato-tangerine accent (Concept B CTA & badges — flat, crisp, no glow)
  static const amber700 = Color(0xFF7C2D12);
  static const amber600 = Color(
    0xFFD94F1A,
  ); // primary CTA orange (AA with white)
  static const amber500 = Color(0xFFE85D26);
  static const amber400 = Color(0xFFF28C5C); // dark-mode culinary accent
  static const amber100 = Color(0xFFFFF1EA);

  // Tertiary — brick terracotta (warnings / expired / negative)
  static const brick700 = Color(0xFF5E2E2F);
  static const brick600 = Color(0xFF763A3B);
  static const brick500 = Color(0xFF8D4D4E);
  static const brick400 = Color(0xFFA96B6C);
  static const brick300 = Color(0xFFE4B2B3);
  static const brick200 = Color(0xFFE6C9C9);
  static const brick100 = Color(0xFFF8E8E8);

  // Functional near-expiry hues (AA-verified on paired bg surfaces)
  static const warnCritical = Color(0xFFB54A1C);
  static const warnSoon = Color(0xFF8C630A);
}

/// Expiry urgency, computed from days-until-expiry (`<=0`, `<=2`, `<=5`, else).
enum ExpiryLevel { expired, critical, soon, ok }

/// The four pantry storage tiers.
enum TierKind { eatSoon, fridge, freezer, pantryShelf }

/// Semantic food-group tint buckets for pantry & recipe rows.
enum CategoryKind { produce, protein, dairyEgg, pantryDry, cooked }

@immutable
class ExpiryColors {
  const ExpiryColors({required this.fg, required this.bg});
  final Color fg;
  final Color bg;
}

@immutable
class TierColors {
  const TierColors({required this.fg, required this.bg});
  final Color fg;
  final Color bg;
}

@immutable
class CategoryColors {
  const CategoryColors({required this.fg, required this.bg});
  final Color fg;
  final Color bg;
}

/// Semantic colours not covered by Material's [ColorScheme].
@immutable
class SweepColors extends ThemeExtension<SweepColors> {
  const SweepColors({
    required this.expired,
    required this.critical,
    required this.soon,
    required this.ok,
    required this.tierEatSoon,
    required this.tierFridge,
    required this.tierFreezer,
    required this.tierPantryShelf,
    required this.catProduce,
    required this.catProtein,
    required this.catDairyEgg,
    required this.catPantryDry,
    required this.catCooked,
    required this.hairline,
    required this.subtleFill,
    required this.surfaceWarm,
    required this.textSecondary,
    required this.textTertiary,
    required this.culinaryAccent,
    required this.culinaryAccentBg,
    required this.onCulinaryAccentBg,
    required this.heroSurface,
    required this.heroSurfaceElevated,
    required this.onHeroSurface,
    required this.onHeroMuted,
    required this.ctaWarm,
    required this.onCtaWarm,
    required this.hangCord,
    required this.successFg,
    required this.successBg,
  });

  final ExpiryColors expired;
  final ExpiryColors critical;
  final ExpiryColors soon;
  final ExpiryColors ok;

  final TierColors tierEatSoon;
  final TierColors tierFridge;
  final TierColors tierFreezer;
  final TierColors tierPantryShelf;

  final CategoryColors catProduce;
  final CategoryColors catProtein;
  final CategoryColors catDairyEgg;
  final CategoryColors catPantryDry;
  final CategoryColors catCooked;

  final Color hairline;
  final Color subtleFill;
  final Color surfaceWarm;
  final Color textSecondary;
  final Color textTertiary;

  final Color culinaryAccent;
  final Color culinaryAccentBg;
  final Color onCulinaryAccentBg;

  final Color heroSurface;
  final Color heroSurfaceElevated;
  final Color onHeroSurface;
  final Color onHeroMuted;
  final Color ctaWarm;
  final Color onCtaWarm;
  final Color hangCord;

  final Color successFg;
  final Color successBg;

  /// Asserting lookup per `design-system-structure`.
  static SweepColors of(BuildContext context) {
    final ext = Theme.of(context).extension<SweepColors>();
    assert(
      ext != null,
      'SweepColors missing from ThemeData. Build ThemeData via AppTheme.',
    );
    return ext!;
  }

  ExpiryColors expiry(ExpiryLevel level) => switch (level) {
    ExpiryLevel.expired => expired,
    ExpiryLevel.critical => critical,
    ExpiryLevel.soon => soon,
    ExpiryLevel.ok => ok,
  };

  TierColors tier(TierKind kind) => switch (kind) {
    TierKind.eatSoon => tierEatSoon,
    TierKind.fridge => tierFridge,
    TierKind.freezer => tierFreezer,
    TierKind.pantryShelf => tierPantryShelf,
  };

  CategoryColors category(CategoryKind kind) => switch (kind) {
    CategoryKind.produce => catProduce,
    CategoryKind.protein => catProtein,
    CategoryKind.dairyEgg => catDairyEgg,
    CategoryKind.pantryDry => catPantryDry,
    CategoryKind.cooked => catCooked,
  };

  CategoryColors categoryForLabel(String rawCategory, {String? fallbackName}) {
    CategoryColors? match(String raw) {
      final c = raw.trim().toLowerCase();
      if (c.isEmpty) return null;
      if (c.contains('rau') ||
          c.contains('trái') ||
          c.contains('củ') ||
          c.contains('cải') ||
          c.contains('hành') ||
          c.contains('cà chua') ||
          c.contains('nấm') ||
          c.contains('tỏi') ||
          c.contains('ớt') ||
          c.contains('khoai') ||
          c.contains('veg') ||
          c.contains('fruit') ||
          c.contains('produce')) {
        return catProduce;
      }
      if (c.contains('thịt') ||
          c.contains('heo') ||
          c.contains('lợn') ||
          c.contains('bò') ||
          c.contains('gà') ||
          c.contains('vịt') ||
          c.contains('cá') ||
          c.contains('tôm') ||
          c.contains('mực') ||
          c.contains('hải sản') ||
          c.contains('meat') ||
          c.contains('pork') ||
          c.contains('beef') ||
          c.contains('chicken') ||
          c.contains('fish') ||
          c.contains('seafood')) {
        return catProtein;
      }
      if (c.contains('trứng') ||
          c.contains('sữa') ||
          c.contains('phô mai') ||
          c.contains('đạm') ||
          c.contains('dairy') ||
          c.contains('egg') ||
          c.contains('milk')) {
        return catDairyEgg;
      }
      if (c.contains('ngũ cốc') ||
          c.contains('gạo') ||
          c.contains('mì') ||
          c.contains('bún') ||
          c.contains('gia vị') ||
          c.contains('khô') ||
          c.contains('dầu') ||
          c.contains('mắm') ||
          c.contains('spice') ||
          c.contains('grain')) {
        return catPantryDry;
      }
      return null;
    }

    return match(rawCategory) ??
        (fallbackName != null ? match(fallbackName) : null) ??
        catCooked;
  }

  static const light = SweepColors(
    expired: ExpiryColors(fg: Color(0xFF8D4D4E), bg: Color(0xFFF8E8E8)),
    critical: ExpiryColors(fg: Color(0xFFB54A1C), bg: Color(0xFFFBEAE1)),
    soon: ExpiryColors(fg: Color(0xFF8C630A), bg: Color(0xFFFBF2DB)),
    ok: ExpiryColors(fg: Color(0xFF535852), bg: Color(0xFFEFECE3)),
    tierEatSoon: TierColors(fg: Color(0xFF8D4D4E), bg: Color(0xFFF8E8E8)),
    tierFridge: TierColors(fg: Color(0xFF255E45), bg: Color(0xFFDFF1E6)),
    tierFreezer: TierColors(fg: Color(0xFF296573), bg: Color(0xFFE1EFF2)),
    tierPantryShelf: TierColors(fg: Color(0xFF73623D), bg: Color(0xFFF3EFE4)),
    catProduce: CategoryColors(fg: Color(0xFF255E45), bg: Color(0xFFE3F2E9)),
    catProtein: CategoryColors(fg: Color(0xFF9C3E32), bg: Color(0xFFFBE9E6)),
    catDairyEgg: CategoryColors(fg: Color(0xFF8C630A), bg: Color(0xFFFBF2DB)),
    catPantryDry: CategoryColors(fg: Color(0xFF6E5B3A), bg: Color(0xFFF3ECE0)),
    catCooked: CategoryColors(fg: Color(0xFF9E4409), bg: Color(0xFFFDF0E4)),
    hairline: Color(0xFFE3DFD5),
    subtleFill: Color(0xFFEFECE3),
    surfaceWarm: Color(0xFFFFFEFA),
    textSecondary: Color(0xFF535852),
    textTertiary: Color(0xFF676C65),
    culinaryAccent: Color(0xFFD94F1A),
    culinaryAccentBg: Color(0xFFFFF1EA),
    onCulinaryAccentBg: Color(0xFF7C2D12),
    heroSurface: Color(0xFF064E3B),
    heroSurfaceElevated: Color(0xFF0D634B),
    onHeroSurface: Color(0xFFFFFFFF),
    onHeroMuted: Color(0xFFB7E8CD),
    ctaWarm: Color(0xFFE0551F),
    onCtaWarm: Color(0xFFFFFFFF),
    hangCord: Color(0xFFE2D7BE),
    successFg: Color(0xFF0B6E4F),
    successBg: Color(0xFFE6F6EE),
  );

  static const dark = SweepColors(
    expired: ExpiryColors(fg: Color(0xFFE4B2B3), bg: Color(0xFF332020)),
    critical: ExpiryColors(fg: Color(0xFFEE9B6D), bg: Color(0xFF352116)),
    soon: ExpiryColors(fg: Color(0xFFE2C167), bg: Color(0xFF302A14)),
    ok: ExpiryColors(fg: Color(0xFFB2BAB1), bg: Color(0xFF202A24)),
    tierEatSoon: TierColors(fg: Color(0xFFE4B2B3), bg: Color(0xFF332020)),
    tierFridge: TierColors(fg: Color(0xFF74D1A1), bg: Color(0xFF183324)),
    tierFreezer: TierColors(fg: Color(0xFF84C4D4), bg: Color(0xFF162B31)),
    tierPantryShelf: TierColors(fg: Color(0xFFCBB88B), bg: Color(0xFF2C2618)),
    catProduce: CategoryColors(fg: Color(0xFF74D1A1), bg: Color(0xFF183324)),
    catProtein: CategoryColors(fg: Color(0xFFF0A197), bg: Color(0xFF36201D)),
    catDairyEgg: CategoryColors(fg: Color(0xFFE2C167), bg: Color(0xFF302A14)),
    catPantryDry: CategoryColors(fg: Color(0xFFCBB88B), bg: Color(0xFF2C2618)),
    catCooked: CategoryColors(fg: Color(0xFFEE9B58), bg: Color(0xFF362213)),
    hairline: Color(0xFF28352E),
    subtleFill: Color(0xFF1C2721),
    surfaceWarm: Color(0xFF16201B),
    textSecondary: Color(0xFFB4BEB6),
    textTertiary: Color(0xFF8D9890),
    culinaryAccent: Color(0xFFF28C5C),
    culinaryAccentBg: Color(0xFF352116),
    onCulinaryAccentBg: Color(0xFFFAC6AC),
    heroSurface: Color(0xFF063B2D),
    heroSurfaceElevated: Color(0xFF0C523E),
    onHeroSurface: Color(0xFFF3F8F5),
    onHeroMuted: Color(0xFFA2DFC0),
    ctaWarm: Color(0xFFE8632B),
    onCtaWarm: Color(0xFFFFFFFF),
    hangCord: Color(0xFFC8BE9F),
    successFg: Color(0xFF6CD4A1),
    successBg: Color(0xFF153224),
  );

  @override
  SweepColors copyWith({
    ExpiryColors? expired,
    ExpiryColors? critical,
    ExpiryColors? soon,
    ExpiryColors? ok,
    TierColors? tierEatSoon,
    TierColors? tierFridge,
    TierColors? tierFreezer,
    TierColors? tierPantryShelf,
    CategoryColors? catProduce,
    CategoryColors? catProtein,
    CategoryColors? catDairyEgg,
    CategoryColors? catPantryDry,
    CategoryColors? catCooked,
    Color? hairline,
    Color? subtleFill,
    Color? surfaceWarm,
    Color? textSecondary,
    Color? textTertiary,
    Color? culinaryAccent,
    Color? culinaryAccentBg,
    Color? onCulinaryAccentBg,
    Color? heroSurface,
    Color? heroSurfaceElevated,
    Color? onHeroSurface,
    Color? onHeroMuted,
    Color? ctaWarm,
    Color? onCtaWarm,
    Color? hangCord,
    Color? successFg,
    Color? successBg,
  }) {
    return SweepColors(
      expired: expired ?? this.expired,
      critical: critical ?? this.critical,
      soon: soon ?? this.soon,
      ok: ok ?? this.ok,
      tierEatSoon: tierEatSoon ?? this.tierEatSoon,
      tierFridge: tierFridge ?? this.tierFridge,
      tierFreezer: tierFreezer ?? this.tierFreezer,
      tierPantryShelf: tierPantryShelf ?? this.tierPantryShelf,
      catProduce: catProduce ?? this.catProduce,
      catProtein: catProtein ?? this.catProtein,
      catDairyEgg: catDairyEgg ?? this.catDairyEgg,
      catPantryDry: catPantryDry ?? this.catPantryDry,
      catCooked: catCooked ?? this.catCooked,
      hairline: hairline ?? this.hairline,
      subtleFill: subtleFill ?? this.subtleFill,
      surfaceWarm: surfaceWarm ?? this.surfaceWarm,
      textSecondary: textSecondary ?? this.textSecondary,
      textTertiary: textTertiary ?? this.textTertiary,
      culinaryAccent: culinaryAccent ?? this.culinaryAccent,
      culinaryAccentBg: culinaryAccentBg ?? this.culinaryAccentBg,
      onCulinaryAccentBg: onCulinaryAccentBg ?? this.onCulinaryAccentBg,
      heroSurface: heroSurface ?? this.heroSurface,
      heroSurfaceElevated: heroSurfaceElevated ?? this.heroSurfaceElevated,
      onHeroSurface: onHeroSurface ?? this.onHeroSurface,
      onHeroMuted: onHeroMuted ?? this.onHeroMuted,
      ctaWarm: ctaWarm ?? this.ctaWarm,
      onCtaWarm: onCtaWarm ?? this.onCtaWarm,
      hangCord: hangCord ?? this.hangCord,
      successFg: successFg ?? this.successFg,
      successBg: successBg ?? this.successBg,
    );
  }

  @override
  SweepColors lerp(covariant SweepColors? other, double t) {
    if (other == null) return this;
    ExpiryColors lerpExpiry(ExpiryColors a, ExpiryColors b) => ExpiryColors(
      fg: Color.lerp(a.fg, b.fg, t)!,
      bg: Color.lerp(a.bg, b.bg, t)!,
    );
    TierColors lerpTier(TierColors a, TierColors b) => TierColors(
      fg: Color.lerp(a.fg, b.fg, t)!,
      bg: Color.lerp(a.bg, b.bg, t)!,
    );
    CategoryColors lerpCat(CategoryColors a, CategoryColors b) =>
        CategoryColors(
          fg: Color.lerp(a.fg, b.fg, t)!,
          bg: Color.lerp(a.bg, b.bg, t)!,
        );
    return SweepColors(
      expired: lerpExpiry(expired, other.expired),
      critical: lerpExpiry(critical, other.critical),
      soon: lerpExpiry(soon, other.soon),
      ok: lerpExpiry(ok, other.ok),
      tierEatSoon: lerpTier(tierEatSoon, other.tierEatSoon),
      tierFridge: lerpTier(tierFridge, other.tierFridge),
      tierFreezer: lerpTier(tierFreezer, other.tierFreezer),
      tierPantryShelf: lerpTier(tierPantryShelf, other.tierPantryShelf),
      catProduce: lerpCat(catProduce, other.catProduce),
      catProtein: lerpCat(catProtein, other.catProtein),
      catDairyEgg: lerpCat(catDairyEgg, other.catDairyEgg),
      catPantryDry: lerpCat(catPantryDry, other.catPantryDry),
      catCooked: lerpCat(catCooked, other.catCooked),
      hairline: Color.lerp(hairline, other.hairline, t)!,
      subtleFill: Color.lerp(subtleFill, other.subtleFill, t)!,
      surfaceWarm: Color.lerp(surfaceWarm, other.surfaceWarm, t)!,
      textSecondary: Color.lerp(textSecondary, other.textSecondary, t)!,
      textTertiary: Color.lerp(textTertiary, other.textTertiary, t)!,
      culinaryAccent: Color.lerp(culinaryAccent, other.culinaryAccent, t)!,
      culinaryAccentBg: Color.lerp(
        culinaryAccentBg,
        other.culinaryAccentBg,
        t,
      )!,
      onCulinaryAccentBg: Color.lerp(
        onCulinaryAccentBg,
        other.onCulinaryAccentBg,
        t,
      )!,
      heroSurface: Color.lerp(heroSurface, other.heroSurface, t)!,
      heroSurfaceElevated: Color.lerp(
        heroSurfaceElevated,
        other.heroSurfaceElevated,
        t,
      )!,
      onHeroSurface: Color.lerp(onHeroSurface, other.onHeroSurface, t)!,
      onHeroMuted: Color.lerp(onHeroMuted, other.onHeroMuted, t)!,
      ctaWarm: Color.lerp(ctaWarm, other.ctaWarm, t)!,
      onCtaWarm: Color.lerp(onCtaWarm, other.onCtaWarm, t)!,
      hangCord: Color.lerp(hangCord, other.hangCord, t)!,
      successFg: Color.lerp(successFg, other.successFg, t)!,
      successBg: Color.lerp(successBg, other.successBg, t)!,
    );
  }
}
