import 'package:frontend/core/error/failure.dart';
import 'package:frontend/features/auth/presentation/controllers/auth_form.dart';
import 'package:frontend/features/auth/presentation/controllers/session_controller.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'login_controller.g.dart';

/// Form state + submit for A-02. UI keeps the text in [TextEditingController]s;
/// this holds only what needs to survive a rebuild (obscure toggle, in-flight
/// flag, server errors).
@riverpod
class LoginController extends _$LoginController {
  @override
  AuthFormState build() => const AuthFormState();

  void toggleObscure() => state = state.copyWith(obscure: !state.obscure);

  /// Returns `true` on success so the screen can navigate.
  Future<bool> submit({required String email, required String password}) async {
    final localErrors = <String, String>{
      if (!isValidEmail(email)) 'email': 'Email không hợp lệ',
      if (password.isEmpty) 'password': 'Nhập mật khẩu',
    };
    if (localErrors.isNotEmpty) {
      state = state.copyWith(fieldErrors: localErrors, formError: null);
      return false;
    }

    state = state.copyWith(
      submitting: true,
      fieldErrors: const {},
      formError: null,
    );
    try {
      await ref
          .read(sessionControllerProvider.notifier)
          .logIn(email: email, password: password);
      return true;
    } on Failure catch (f) {
      state = state.copyWith(submitting: false, formError: f.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        submitting: false,
        formError: 'Đăng nhập không thành công. Thử lại nhé.',
      );
      return false;
    }
  }
}
