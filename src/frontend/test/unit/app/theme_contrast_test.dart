import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_theme.dart';

double _contrastRatio(Color a, Color b) {
  final la = a.computeLuminance();
  final lb = b.computeLuminance();
  final hi = la > lb ? la : lb;
  final lo = la > lb ? lb : la;
  return (hi + 0.05) / (lo + 0.05);
}

void main() {
  group('Design System 2.0 contrast & parity', () {
    test(
      'light and dark ColorSchemes and SweepColors meet WCAG AA (4.5:1)',
      () {
        for (final theme in [AppTheme.light, AppTheme.dark]) {
          final cs = theme.colorScheme;
          final sweep = theme.extension<SweepColors>()!;

          // Surface text contrast
          expect(
            _contrastRatio(cs.onSurface, cs.surface),
            greaterThanOrEqualTo(4.5),
          );
          expect(
            _contrastRatio(cs.onSurface, cs.surfaceContainerLowest),
            greaterThanOrEqualTo(4.5),
          );
          expect(
            _contrastRatio(sweep.textSecondary, cs.surfaceContainerLowest),
            greaterThanOrEqualTo(4.5),
          );
          expect(
            _contrastRatio(sweep.textTertiary, cs.surfaceContainerLowest),
            greaterThanOrEqualTo(4.5),
          );

          // Button / container pairings
          expect(
            _contrastRatio(cs.onPrimary, cs.primary),
            greaterThanOrEqualTo(4.5),
          );
          expect(
            _contrastRatio(cs.onPrimaryContainer, cs.primaryContainer),
            greaterThanOrEqualTo(4.5),
          );

          // Expiry semantic pairs
          for (final lvl in ExpiryLevel.values) {
            final pair = sweep.expiry(lvl);
            expect(
              _contrastRatio(pair.fg, pair.bg),
              greaterThanOrEqualTo(4.5),
              reason: 'Expiry $lvl contrast failed in ${theme.brightness}',
            );
          }

          // Storage tier semantic pairs
          for (final tier in TierKind.values) {
            final pair = sweep.tier(tier);
            expect(
              _contrastRatio(pair.fg, pair.bg),
              greaterThanOrEqualTo(4.5),
              reason: 'Tier $tier contrast failed in ${theme.brightness}',
            );
          }

          // Food-group category pairs
          for (final cat in CategoryKind.values) {
            final pair = sweep.category(cat);
            expect(
              _contrastRatio(pair.fg, pair.bg),
              greaterThanOrEqualTo(4.5),
              reason: 'Category $cat contrast failed in ${theme.brightness}',
            );
          }

          // Culinary accent pair
          expect(
            _contrastRatio(sweep.onCulinaryAccentBg, sweep.culinaryAccentBg),
            greaterThanOrEqualTo(4.5),
          );
        }
      },
    );
  });
}
