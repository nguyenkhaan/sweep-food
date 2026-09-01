import 'package:flutter/widgets.dart';

/// Spacing scale (from the design "Foundations" artboard).
abstract final class Gap {
  static const xxs = 4.0;
  static const xs = 8.0;
  static const sm = 12.0;
  static const md = 16.0;
  static const lg = 20.0;
  static const xl = 24.0;
  static const xxl = 32.0;
  static const xxxl = 40.0;

  static const gapXxs = SizedBox(width: xxs, height: xxs);
  static const gapXs = SizedBox(width: xs, height: xs);
  static const gapSm = SizedBox(width: sm, height: sm);
  static const gapMd = SizedBox(width: md, height: md);
  static const gapLg = SizedBox(width: lg, height: lg);
  static const gapXl = SizedBox(width: xl, height: xl);
}

/// Corner radii.
abstract final class Radii {
  static const sm = 8.0; // controls
  static const md = 12.0;
  static const lg = 16.0; // cards
  static const xl = 24.0; // bottom sheets
  static const pill = 999.0;

  static const brSm = BorderRadius.all(Radius.circular(sm));
  static const brMd = BorderRadius.all(Radius.circular(md));
  static const brLg = BorderRadius.all(Radius.circular(lg));
  static const brXl = BorderRadius.all(Radius.circular(xl));
  static const brSheet = BorderRadius.vertical(top: Radius.circular(xl));
}

/// Elevation shadows (e1 = card, e2 = raised, e3 = sheet / FAB).
abstract final class Shadows {
  static const e1 = <BoxShadow>[
    BoxShadow(color: Color(0x0F141C16), blurRadius: 3, offset: Offset(0, 1)),
    BoxShadow(color: Color(0x0A141C16), blurRadius: 2, offset: Offset(0, 1)),
  ];
  static const e2 = <BoxShadow>[
    BoxShadow(color: Color(0x14141C16), blurRadius: 10, offset: Offset(0, 2)),
  ];
  static const e3 = <BoxShadow>[
    BoxShadow(color: Color(0x24141C16), blurRadius: 26, offset: Offset(0, 10)),
  ];
}

/// Common edge insets.
abstract final class Insets {
  static const screenH = EdgeInsets.symmetric(horizontal: Gap.lg);
  static const card = EdgeInsets.all(Gap.md);
  static const sheet = EdgeInsets.fromLTRB(Gap.lg, Gap.sm, Gap.lg, Gap.xl);
}

/// Minimum interactive hit target.
const double kMinTapTarget = 44.0;
