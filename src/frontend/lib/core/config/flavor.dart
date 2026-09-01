/// Build flavor, selected via `--dart-define-from-file=config/<flavor>.json`.
enum Flavor {
  dev,
  prod;

  static Flavor fromName(String value) => Flavor.values.firstWhere(
        (f) => f.name == value,
        orElse: () => Flavor.dev,
      );

  bool get isDev => this == Flavor.dev;
  bool get isProd => this == Flavor.prod;
}

/// Which API implementation the app talks to.
enum Backend {
  /// Serve responses from `assets/mock/*.json`.
  mock,

  /// Real HTTP backend via Dio.
  live;

  static Backend fromName(String value) => Backend.values.firstWhere(
        (b) => b.name == value,
        orElse: () => Backend.mock,
      );

  bool get isMock => this == Backend.mock;
}
