import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';

/// Shared app logger. Verbose in debug, warnings-and-up in release.
final Logger log = Logger(
  level: kReleaseMode ? Level.warning : Level.debug,
  printer: PrettyPrinter(
    methodCount: 0,
    errorMethodCount: 6,
    lineLength: 90,
    colors: true,
    printEmojis: true,
    dateTimeFormat: DateTimeFormat.onlyTimeAndSinceStart,
  ),
);
