import 'package:flutter/material.dart';

/// Brand + neutral palette (from the design "Foundations" artboard).
///
/// Values that map cleanly onto Material's [ColorScheme] are wired there in
/// [AppTheme]; the rest — expiry-state and storage-tier colours — live in the
/// [SweepColors] theme extension below and are read via
/// `Theme.of(context).extension<SweepColors>()!` (or `context.sweep`).
abstract final class BrandPalette {
  // Primary — green
  static const green900 = Color(0xFF14352A);
  static const green800 = Color(0xFF1B4332);
  static const green700 = Color(0xFF2D6A4F); // primary
  static const green600 = Color(0xFF40916C);
  static const green500 = Color(0xFF52B788);
  static const green400 = Color(0xFF74C69D);
  static const green300 = Color(0xFF95D5B2); // secondary
  static const green200 = Color(0xFFB7E4C7);
  static const green100 = Color(0xFFD8F3DC);

  // Tertiary — brick red (warnings / expired / negative)
  static const brick700 = Color(0xFF5E2E2F);
  static const brick600 = Color(0xFF763A3B);
  static const brick500 = Color(0xFF8D4D4E);
  static const brick400 = Color(0xFFA96B6C);
  static const brick300 = Color(0xFFC99A9B);
  static const brick200 = Color(0xFFE6C9C9);
  static const brick100 = Color(0xFFF6E7E7);

  // Functional status hues (not brand colours) — near-expiry scale
  static const warnCritical = Color(0xFFC0562B);
  static const warnSoon = Color(0xFFB08422);
}

/// Expiry urgency, computed from days-until-expiry (`<=0`, `<=2`, `<=5`, else).
enum ExpiryLevel { expired, critical, soon, ok }

/// The four pantry storage tiers.
enum TierKind { eatSoon, fridge, freezer, pantryShelf }

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

/// Semantic colours not covered by [ColorScheme].
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
    required this.hairline,
    required this.subtleFill,
    required this.textSecondary,
    required this.textTertiary,
  });

  final ExpiryColors expired;
  final ExpiryColors critical;
  final ExpiryColors soon;
  final ExpiryColors ok;

  final TierColors tierEatSoon;
  final TierColors tierFridge;
  final TierColors tierFreezer;
  final TierColors tierPantryShelf;

  final Color hairline;
  final Color subtleFill;
  final Color textSecondary;
  final Color textTertiary;

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

  static const light = SweepColors(
    expired: ExpiryColors(fg: Color(0xFF8D4D4E), bg: Color(0xFFF6E7E7)),
    critical: ExpiryColors(fg: Color(0xFFC0562B), bg: Color(0xFFF7E9E0)),
    soon: ExpiryColors(fg: Color(0xFFB08422), bg: Color(0xFFFBF3E2)),
    ok: ExpiryColors(fg: Color(0xFF5C5F5A), bg: Color(0xFFEFF1EC)),
    tierEatSoon: TierColors(fg: Color(0xFF8D4D4E), bg: Color(0xFFF6E7E7)),
    tierFridge: TierColors(fg: Color(0xFF2D6A4F), bg: Color(0xFFE4F3EB)),
    tierFreezer: TierColors(fg: Color(0xFF3E7C8B), bg: Color(0xFFE3EFF1)),
    tierPantryShelf: TierColors(fg: Color(0xFF8A7A55), bg: Color(0xFFF2EFE8)),
    hairline: Color(0xFFE1E3DE),
    subtleFill: Color(0xFFEFF1EC),
    textSecondary: Color(0xFF5C5F5A),
    textTertiary: Color(0xFF8A8D87),
  );

  static const dark = SweepColors(
    expired: ExpiryColors(fg: Color(0xFFD9A7A8), bg: Color(0xFF33211F)),
    critical: ExpiryColors(fg: Color(0xFFE08A5C), bg: Color(0xFF352017)),
    soon: ExpiryColors(fg: Color(0xFFD6B45A), bg: Color(0xFF312B16)),
    ok: ExpiryColors(fg: Color(0xFFA8ADA4), bg: Color(0xFF242B25)),
    tierEatSoon: TierColors(fg: Color(0xFFC99A9B), bg: Color(0xFF33211F)),
    tierFridge: TierColors(fg: Color(0xFF74C69D), bg: Color(0xFF17301F)),
    tierFreezer: TierColors(fg: Color(0xFF7FB6C4), bg: Color(0xFF16292E)),
    tierPantryShelf: TierColors(fg: Color(0xFFB9A87E), bg: Color(0xFF2A2519)),
    hairline: Color(0xFF2E362F),
    subtleFill: Color(0xFF242B25),
    textSecondary: Color(0xFFA8ADA4),
    textTertiary: Color(0xFF7C827A),
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
    Color? hairline,
    Color? subtleFill,
    Color? textSecondary,
    Color? textTertiary,
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
      hairline: hairline ?? this.hairline,
      subtleFill: subtleFill ?? this.subtleFill,
      textSecondary: textSecondary ?? this.textSecondary,
      textTertiary: textTertiary ?? this.textTertiary,
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
    return SweepColors(
      expired: lerpExpiry(expired, other.expired),
      critical: lerpExpiry(critical, other.critical),
      soon: lerpExpiry(soon, other.soon),
      ok: lerpExpiry(ok, other.ok),
      tierEatSoon: lerpTier(tierEatSoon, other.tierEatSoon),
      tierFridge: lerpTier(tierFridge, other.tierFridge),
      tierFreezer: lerpTier(tierFreezer, other.tierFreezer),
      tierPantryShelf: lerpTier(tierPantryShelf, other.tierPantryShelf),
      hairline: Color.lerp(hairline, other.hairline, t)!,
      subtleFill: Color.lerp(subtleFill, other.subtleFill, t)!,
      textSecondary: Color.lerp(textSecondary, other.textSecondary, t)!,
      textTertiary: Color.lerp(textTertiary, other.textTertiary, t)!,
    );
  }
}
