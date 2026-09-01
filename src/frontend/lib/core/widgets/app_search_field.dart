import 'package:flutter/material.dart';

/// Rounded search input used on Kho / Gợi ý / catalog pickers.
class AppSearchField extends StatelessWidget {
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
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      onChanged: onChanged,
      onSubmitted: onSubmitted,
      textInputAction: TextInputAction.search,
      decoration: InputDecoration(
        hintText: hintText,
        prefixIcon: const Icon(Icons.search_rounded, size: 20),
        isDense: true,
      ),
    );
  }
}
