import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';

class CreateEditMenuDialog extends StatefulWidget {
  const CreateEditMenuDialog({
    this.initialName,
    this.initialDescription,
    this.title = 'Tạo thực đơn yêu thích',
    this.actionLabel = 'Tạo',
    super.key,
  });

  final String? initialName;
  final String? initialDescription;
  final String title;
  final String actionLabel;

  static Future<({String name, String? description})?> show(
    BuildContext context, {
    String? initialName,
    String? initialDescription,
    String title = 'Tạo thực đơn yêu thích',
    String actionLabel = 'Tạo',
  }) {
    return showDialog<({String name, String? description})>(
      context: context,
      builder: (_) => CreateEditMenuDialog(
        initialName: initialName,
        initialDescription: initialDescription,
        title: title,
        actionLabel: actionLabel,
      ),
    );
  }

  @override
  State<CreateEditMenuDialog> createState() => _CreateEditMenuDialogState();
}

class _CreateEditMenuDialogState extends State<CreateEditMenuDialog> {
  late final TextEditingController _nameCtrl;
  late final TextEditingController _descCtrl;

  @override
  void initState() {
    super.initState();
    _nameCtrl = TextEditingController(text: widget.initialName);
    _descCtrl = TextEditingController(text: widget.initialDescription);
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.title),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _nameCtrl,
              autofocus: true,
              decoration: const InputDecoration(
                labelText: 'Tên thực đơn *',
                hintText: 'Ví dụ: Bữa cơm gia đình, Món ăn Eat Clean',
              ),
              textCapitalization: TextCapitalization.sentences,
            ),
            Gap.gapMd,
            TextField(
              controller: _descCtrl,
              decoration: const InputDecoration(
                labelText: 'Mô tả (tùy chọn)',
                hintText: 'Ghi chú về thực đơn này...',
              ),
              maxLines: 2,
              textCapitalization: TextCapitalization.sentences,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Hủy'),
        ),
        FilledButton(
          onPressed: () {
            final name = _nameCtrl.text.trim();
            if (name.isEmpty) return;
            final desc = _descCtrl.text.trim();
            Navigator.of(context).pop((
              name: name,
              description: desc.isNotEmpty ? desc : null,
            ));
          },
          child: Text(widget.actionLabel),
        ),
      ],
    );
  }
}
