import 'package:flutter/foundation.dart';

/// Shared state for the login / register / forgot-password forms (A-02..A-04).
///
/// The text itself lives in the screens' [TextEditingController]s; this carries
/// only what must survive a rebuild: the password-visibility toggle, the
/// in-flight flag, a form-level error banner, and per-field errors (422).
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

final _emailRe = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

bool isValidEmail(String value) => _emailRe.hasMatch(value.trim());

/// Plan.md §9 / design copy: "Ít nhất 8 ký tự".
bool isValidPassword(String value) => value.length >= 8;
