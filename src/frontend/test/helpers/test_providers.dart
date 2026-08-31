// test/helpers/test_providers.dart
// ProviderContainer helpers + repository overrides for widget/controller tests.
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart' show Override;
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/config/app_config.dart';
import 'package:sweepfood/core/config/app_config_provider.dart';
import 'package:sweepfood/core/config/flavor.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/network_providers.dart';

/// A [ProviderContainer] with the given [overrides], auto-disposed after the test.
ProviderContainer createContainer({List<Override> overrides = const []}) {
  final container = ProviderContainer(overrides: overrides);
  addTearDown(container.dispose);
  return container;
}

/// Points the app at a fake [ApiClient] and a mock/dev [AppConfig].
List<Override> apiOverrides(ApiClient client) => [
      apiClientProvider.overrideWithValue(client),
      appConfigProvider.overrideWithValue(
        const AppConfig(
          flavor: Flavor.dev,
          backend: Backend.mock,
          apiBaseUrl: 'http://test/api/v1',
          premiumEnabled: false,
          nearExpiryDays: 3,
          fcmEnabled: false,
        ),
      ),
    ];
