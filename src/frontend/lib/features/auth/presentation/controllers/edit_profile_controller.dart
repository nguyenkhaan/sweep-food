import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/presentation/controllers/auth_form.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'edit_profile_controller.g.dart';

/// P-01a — edit the signed-in user's display name via `PATCH /users/profile`.
/// On success the [SessionController] cache is refreshed from the response.
@riverpod
class EditProfileController extends _$EditProfileController {
  @override
  AuthFormState build() => const AuthFormState();

  /// Returns `true` on success so the screen can pop.
  Future<bool> submit({required String name, required AppL10n l10n}) async {
    final trimmed = name.trim();
    if (trimmed.isEmpty) {
      state = state.copyWith(
        fieldErrors: {'name': l10n.authEnterName},
        formError: null,
      );
      return false;
    }

    state = state.copyWith(
      submitting: true,
      fieldErrors: const {},
      formError: null,
    );
    final res =
        await ref.read(authRepositoryProvider).updateProfile(name: trimmed);
    return res.fold(
      (f) {
        state = state.copyWith(
          submitting: false,
          formError: f.localizedMessage(l10n),
        );
        return false;
      },
      (user) {
        ref.read(sessionControllerProvider.notifier).applyUpdatedUser(user);
        state = state.copyWith(submitting: false);
        return true;
      },
    );
  }
}
