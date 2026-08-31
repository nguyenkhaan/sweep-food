import 'package:flutter/foundation.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

enum PantryMemberRole { owner, editor }

enum PantryMemberStatus { active, invited }

/// A member of a shared pantry (P-05). Sharing itself is **"Sắp có"** in the
/// MVP — this only backs the locked preview.
@immutable
class PantryMember {
  const PantryMember({
    required this.name,
    required this.role,
    this.status = PantryMemberStatus.active,
  });

  final String name;
  final PantryMemberRole role;
  final PantryMemberStatus status;

  String get initials => name.trim().isEmpty
      ? '?'
      : name.trim().split(RegExp(r'\s+')).last.substring(0, 1).toUpperCase();

  String roleLabel(AppL10n l10n) => switch (status) {
    PantryMemberStatus.invited => l10n.pantryMemberInvited,
    _ => switch (role) {
      PantryMemberRole.owner => l10n.pantryRoleOwner,
      PantryMemberRole.editor => l10n.pantryRoleEditor,
    },
  };
}
