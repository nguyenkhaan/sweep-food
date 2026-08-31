import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

part 'user.freezed.dart';

/// The signed-in account. UI-facing, immutable.
///
/// Backend contract (`docs/api-contract.md` §1): sign-in is by **phone (E.164)**
/// + password. `GET /users/profile` is the source — [name]/[email] are optional
/// there, and [dietaryPreference]/[avatarUrl] are read from its free-form
/// `preferences` map.
@freezed
abstract class User with _$User {
  const User._();

  const factory User({
    required String id,
    required String phone,
    String? name,
    String? email,
    DietaryPreference? dietaryPreference,
    String? avatarUrl,
  }) = _User;

  /// First name / display handle for the greeting header (H-01).
  String get displayName {
    final n = name?.trim() ?? '';
    return n.isEmpty ? 'bạn' : n;
  }

  /// Initials for the avatar fallback ("Nguyễn Văn A" → "A").
  String get initials {
    final parts = (name ?? '')
        .trim()
        .split(RegExp(r'\s+'))
        .where((p) => p.isNotEmpty)
        .toList();
    if (parts.isEmpty) return '?';
    return parts.last.substring(0, 1).toUpperCase();
  }
}
