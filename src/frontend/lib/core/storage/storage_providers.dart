import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:frontend/core/storage/secure_storage.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'storage_providers.g.dart';

@Riverpod(keepAlive: true)
FlutterSecureStorage flutterSecureStorage(Ref ref) =>
    const FlutterSecureStorage();

@Riverpod(keepAlive: true)
SecureStore secureStore(Ref ref) =>
    SecureStore(ref.watch(flutterSecureStorageProvider));
