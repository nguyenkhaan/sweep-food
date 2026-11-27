import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/auth/presentation/controllers/edit_profile_controller.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_form_error.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_text_field.dart';

/// P-01a — edit the signed-in user's display name (Concept B · Format 1).
class EditProfileScreen extends ConsumerStatefulWidget {
  const EditProfileScreen({super.key});

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  late final TextEditingController _name;

  @override
  void initState() {
    super.initState();
    final user = ref.read(sessionControllerProvider).asData?.value?.user;
    _name = TextEditingController(text: user?.name ?? '');
  }

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    FocusScope.of(context).unfocus();
    final ok = await ref
        .read(editProfileControllerProvider.notifier)
        .submit(name: _name.text, l10n: context.l10n);
    if (ok && mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(context.l10n.editProfileSaved)));
      context.pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final state = ref.watch(editProfileControllerProvider);

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: context.colors.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(title: l10n.editProfileTitle),
            Expanded(
              child: SafeArea(
                top: false,
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(
                    Gap.lg,
                    Gap.sm,
                    Gap.lg,
                    Gap.xl,
                  ),
                  children: [
                    Container(
                      padding: const EdgeInsets.all(Gap.md),
                      decoration: BoxDecoration(
                        color: context.colors.surfaceContainerLowest,
                        borderRadius: Radii.brXl,
                        border: Border.all(color: context.sweep.hairline),
                        boxShadow: Shadows.e1,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          AuthTextField(
                            label: l10n.editProfileNameLabel,
                            controller: _name,
                            hintText: l10n.authFullNameHint,
                            prefixIcon: AppIcons.profile,
                            textCapitalization: TextCapitalization.words,
                            textInputAction: TextInputAction.done,
                            onSubmitted: (_) => _submit(),
                            errorText: state.fieldErrors['name'],
                          ),
                          if (state.formError != null) ...[
                            Gap.gapXs,
                            AuthFormError(state.formError!),
                          ],
                          Gap.gapLg,
                          PrimaryButton(
                            label: l10n.commonSave,
                            loading: state.submitting,
                            onPressed: state.submitting ? null : _submit,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
