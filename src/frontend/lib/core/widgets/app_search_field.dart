import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Rounded search input used on Kho / Gợi ý / catalog pickers.
class AppSearchField extends StatefulWidget {
  const AppSearchField({
    required this.hintText,
    this.controller,
    this.onChanged,
    this.onSubmitted,
    super.key,
  });

  final String hintText;
  final TextEditingController? controller;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;

  @override
  State<AppSearchField> createState() => _AppSearchFieldState();
}

class _AppSearchFieldState extends State<AppSearchField> {
  late final TextEditingController _ownController;
  TextEditingController get _ctrl => widget.controller ?? _ownController;

  @override
  void initState() {
    super.initState();
    _ownController = TextEditingController();
    _ctrl.addListener(_onTextChange);
  }

  @override
  void dispose() {
    _ctrl.removeListener(_onTextChange);
    if (widget.controller == null) _ownController.dispose();
    super.dispose();
  }

  void _onTextChange() {
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final hasText = _ctrl.text.isNotEmpty;
    return TextField(
      controller: _ctrl,
      onChanged: widget.onChanged,
      onSubmitted: widget.onSubmitted,
      textInputAction: TextInputAction.search,
      decoration: InputDecoration(
        hintText: widget.hintText,
        prefixIcon: Icon(
          AppIcons.search,
          size: 19,
          color: context.sweep.textTertiary,
        ),
        suffixIcon: hasText
            ? IconButton(
                tooltip: context.l10n.commonClose,
                icon: Icon(
                  AppIcons.close,
                  size: 17,
                  color: context.sweep.textTertiary,
                ),
                onPressed: () {
                  AppHaptics.selection();
                  _ctrl.clear();
                  widget.onChanged?.call('');
                },
              )
            : null,
        isDense: true,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: Gap.md,
          vertical: Gap.sm,
        ),
      ),
    );
  }
}
