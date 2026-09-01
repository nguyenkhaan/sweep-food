import 'package:flutter/foundation.dart';

/// Shared state for the login / register / OTP / reset-password forms
/// (A-02..A-04 + OTP).
///
/// The text itself lives in the screens' [TextEditingController]s; this carries
/// only what must survive a rebuild: the password-visibility toggle, the
/// in-flight flag, a form-level error banner, and per-field errors.
@immutable
class AuthFormState {
  const AuthFormState({
    this.obscure = true,
    this.submitting = false,
    this.formError,
    this.fieldErrors = const {},
  });

  final bool obscure;
  final bool submitting;
  final String? formError;
  final Map<String, String> fieldErrors;

  bool get hasFieldErrors => fieldErrors.isNotEmpty;

  AuthFormState copyWith({
    bool? obscure,
    bool? submitting,
    Object? formError = _sentinel,
    Map<String, String>? fieldErrors,
  }) {
    return AuthFormState(
      obscure: obscure ?? this.obscure,
      submitting: submitting ?? this.submitting,
      formError:
          identical(formError, _sentinel) ? this.formError : formError as String?,
      fieldErrors: fieldErrors ?? this.fieldErrors,
    );
  }

  static const _sentinel = Object();
}

final _e164Re = RegExp(r'^\+[1-9]\d{7,14}$');

/// Best-effort normalisation of a Vietnamese phone number to E.164, matching the
/// backend's `^\+[1-9][0-9]{7,14}$` rule. `0901234567` → `+84901234567`.
String normalizePhoneE164(String raw) {
  var s = raw.replaceAll(RegExp(r'[\s\-().]'), '');
  if (s.startsWith('00')) s = '+${s.substring(2)}';
  if (s.startsWith('+')) return s;
  if (s.startsWith('0')) return '+84${s.substring(1)}';
  if (s.startsWith('84')) return '+$s';
  return '+84$s';
}

/// Whether [raw], once normalised, is a valid E.164 number the backend accepts.
bool isValidPhone(String raw) => _e164Re.hasMatch(normalizePhoneE164(raw));

/// Plan.md §9 / design copy: "Ít nhất 8 ký tự".
bool isValidPassword(String value) => value.length >= 8;

/// The backend OTP is always six digits.
bool isValidOtp(String value) => RegExp(r'^\d{6}$').hasMatch(value.trim());
