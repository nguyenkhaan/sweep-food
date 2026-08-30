import 'package:frontend/core/config/app_config.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'app_config_provider.g.dart';

/// The app-wide [AppConfig]. Overridden in `bootstrap()` with the instance read
/// from `--dart-define`; the fallback here keeps tests / previews working.
@Riverpod(keepAlive: true)
AppConfig appConfig(Ref ref) => AppConfig.fromEnvironment();
