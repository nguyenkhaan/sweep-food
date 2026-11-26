---
name: sweepfood-design-system
description: >-
  Enforces SweepFood's Material 3 visual tokens (`AppTheme`, `SweepColors`,
  `BrandPalette`, `AppTypography`, `Gap`, `Radii`, `Insets`, `Shadows`), Light
  and Dark mode parity, Vietnamese typography safety, and reuse of shared
  widgets in `src/frontend/lib/core/widgets/`. Use whenever building,
  polishing, redesigning, or reviewing any Flutter screen, bottom sheet,
  dialog, card, or UI component in `src/frontend/`.
---

# SweepFood Design System & Mobile UI Guide

All visual styling in `src/frontend/` derives from the design foundations in `lib/app/theme/`. Never hardcode raw hex colors, `Colors.*`, raw spacing numbers, or ad-hoc border radii inside feature screens or widgets.

## 1. Design Tokens (Single Source of Truth)

Import `package:sweepfood/core/utils/extensions/build_context_x.dart` and `package:sweepfood/app/theme/app_spacing.dart` to read tokens cleanly:

| Need | Use | Source |
| :--- | :--- | :--- |
| Surface, primary, error, outline colors | `context.colors` (`ColorScheme`) | `lib/app/theme/app_theme.dart` |
| Semantic expiry & storage tier colors, hairlines, muted text | `context.sweep` (`SweepColors`) | `lib/app/theme/app_colors.dart` |
| Expiry urgency (`<=0`, `<=2`, `<=5`, else) | `context.sweep.expiry(ExpiryLevel.*)` (`fg` + `bg`) | `lib/app/theme/app_colors.dart` |
| Storage tier tint (`eatSoon`, `fridge`, `freezer`, `pantryShelf`) | `context.sweep.tier(TierKind.*)` (`fg` + `bg`) | `lib/app/theme/app_colors.dart` |
| Typography (`Inter` scale) | `context.text` (`displaySmall`..`labelSmall`) | `lib/app/theme/app_typography.dart` |
| Spacing & gaps | `Gap.xxs` (4) .. `Gap.xxxl` (40), `Gap.gapXs`..`Gap.gapXl` | `lib/app/theme/app_spacing.dart` |
| Corner radii | `Radii.brSm` (8), `brMd` (12), `brLg` (16 cards), `brXl` (24), `brSheet`, `Radii.pill` | `lib/app/theme/app_spacing.dart` |
| Standard padding | `Insets.screenH`, `Insets.card`, `Insets.sheet` | `lib/app/theme/app_spacing.dart` |
| Shadows | `Shadows.e1` (card), `e2` (raised), `e3` (sheet/FAB) | `lib/app/theme/app_spacing.dart` |
| Tap target floor | `kMinTapTarget` (`44.0`, prefer `48.0` for primary touch targets) | `lib/app/theme/app_spacing.dart` |

**Brand identity:**
- Primary green: `BrandPalette.green700` (`#2D6A4F`) in Light, `BrandPalette.green600` (`#40916C`) in Dark.
- Warning / destructive brick red: `BrandPalette.brick500` (`#8D4D4E`) in Light, `BrandPalette.brick300` (`#C99A9B`) in Dark.
- Cards use `surfaceContainerLowest` + `1px` `sweep.hairline` border (`elevation: 0`), not heavy drop shadows.

## 2. Reuse Shared Widgets Before Creating New Ones

Check `src/frontend/lib/core/widgets/` first—SweepFood already provides 28 production widgets:

- **Screen & Chrome:** `AppScaffold`, `AppBottomNav`, `AppBottomSheet`, `QuickActionSheet`, `AppFab`, `SectionHeader`, `QuotaBanner`
- **Buttons & Inputs:** `PrimaryButton`, `SecondaryButton`, `AppTextButton`, `AppIconButton`, `AppSearchField`, `FilterChipRow`, `ConfidenceField`
- **Async & Feedback:** `AsyncValueWidget`, `LoadingSkeleton`, `EmptyState`, `ErrorView`, `AppSnackBar` (or `context.showSnack(...)`)
- **Domain Components:** `PantryItemCard`, `SuggestionCard`, `ExpiryBadge`, `TierChip`, `MacroRing`, `MacroChips`, `RecipeImage`, `WasteSavedPill`, `WaveformRecorder`

Extract reusable feature widgets as named `const` `StatelessWidget` classes rather than private `Widget _buildX()` methods.

## 3. Light & Dark Mode Parity

- Every screen must look intentional in both `AppTheme.light` and `AppTheme.dark`.
- Never use `Colors.white`, `Colors.black`, or `Colors.grey` for surfaces, borders, or text—use `context.colors.surface*`, `context.colors.onSurface`, `context.sweep.textSecondary`, `context.sweep.textTertiary`, and `context.sweep.hairline`.
- Verify expiry/tier badges use paired `fg` + `bg` from `context.sweep.expiry(...)` / `context.sweep.tier(...)` so contrast stays readable in dark mode.

## 4. Vietnamese Copy, Localization & Accessibility

- Always render strings through `context.l10n.<key>` (`lib/l10n/app_vi.arb` + `app_en.arb`).
- Render `Failure` objects via `failure.localizedMessage(context.l10n)` or `context.saveErrorMessage(error)`.
- **Vietnamese text is typically 15–30% longer than English** and has stacked diacritics (`ế`, `ộ`, `ử`). Avoid cramped fixed-width containers, never clamp `MediaQuery` text scaling, and let labels wrap or scroll cleanly with `Flexible`/`Expanded`.
- Never rely on color alone for expiry urgency or status—pair color with icon + explicit text label (`ExpiryBadge`, `TierChip`).
- Respect `kMinTapTarget` (`>= 44dp`, ideally `48dp`) on all interactive controls and provide `Semantics` labels for icon-only buttons.

## 5. Verification Checklist

Before completing UI work:
1. Confirm zero raw `Color(0x...)` or `Colors.*` literals introduced outside `lib/app/theme/`.
2. Check both Light and Dark themes (via widget preview, emulator, or widget tests).
3. Verify keyboard / IME avoidance (`resizeToAvoidBottomInset`, scrollable form content) on input screens and bottom sheets.
4. Run `dart format .`, `flutter analyze`, and affected widget tests in `src/frontend/test/widget/`.
