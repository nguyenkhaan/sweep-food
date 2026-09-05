import 'dart:math';

/// Generates `Idempotency-Key` header values for backend write endpoints that
/// require one (Inventory, Shopping List — see `docs/api-contract.md`).
///
/// A v4-shaped UUID is enough here: the backend only needs the key to be
/// unique per logical write attempt, not RFC-4122 compliant.
abstract final class Idempotency {
  static final _random = Random.secure();

  static String newKey() {
    final bytes = List<int>.generate(16, (_) => _random.nextInt(256));
    bytes[6] = (bytes[6] & 0x0f) | 0x40; // version 4
    bytes[8] = (bytes[8] & 0x3f) | 0x80; // variant 1

    String hex(Iterable<int> b) =>
        b.map((v) => v.toRadixString(16).padLeft(2, '0')).join();

    return '${hex(bytes.sublist(0, 4))}-${hex(bytes.sublist(4, 6))}-'
        '${hex(bytes.sublist(6, 8))}-${hex(bytes.sublist(8, 10))}-'
        '${hex(bytes.sublist(10, 16))}';
  }
}
