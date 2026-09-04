import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/notifications/data/datasources/device_remote_data_source.dart';
import 'package:sweepfood/features/notifications/domain/repositories/device_repository.dart';

part 'device_repository_impl.g.dart';

@Riverpod(keepAlive: true)
DeviceRepository deviceRepository(Ref ref) =>
    DeviceRepositoryImpl(DeviceRemoteDataSource(ref.watch(apiClientProvider)));

class DeviceRepositoryImpl implements DeviceRepository {
  DeviceRepositoryImpl(this._remote);

  final DeviceRemoteDataSource _remote;

  @override
  Future<Result<String>> register(String fcmToken, {required String platform}) =>
      runGuarded(() => _remote.register(fcmToken, platform: platform));

  @override
  Future<Result<void>> unregister(String deviceId) =>
      guardVoid(() => _remote.unregister(deviceId));
}
