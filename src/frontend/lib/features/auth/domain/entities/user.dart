import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

part 'user.freezed.dart';

/// The signed-in account (spec §9 domain model). UI-facing, immutable.
///
/// NOTE: the frontend's assumed contract (plan.md §9 + the design canvas) is
/// email + password. The current backend stub authenticates with phone + OTP —
/// reconciled in M6 via `docs/api-contract.md`. Until then `MockApiClient`
/// serves `assets/mock/auth_*.json` and this shape is the source of truth.
@freezed
abstract class User with _$User {
  const User._();

  const factory User({
    required String id,
    required String name,
    required String email,
    DietaryPreference? dietaryPreference,
    String? avatarUrl,
  }) = _User;

  /// First name / display handle for the greeting header (H-01).
  String get displayName => name.trim().isEmpty ? 'bạn' : name.trim();

  /// Initials for the avatar fallback ("Nguyễn Văn A" → "A").
  String get initials {
    final parts =
        name.trim().split(RegExp(r'\s+')).where((p) => p.isNotEmpty).toList();
    if (parts.isEmpty) return '?';
    return parts.last.substring(0, 1).toUpperCase();
  }
}
