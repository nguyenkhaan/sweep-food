import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_bottom_sheet.dart';
import 'package:frontend/core/widgets/app_snackbar.dart';
import 'package:frontend/features/cooking/domain/entities/cooked_food.dart';
import 'package:frontend/features/cooking/presentation/controllers/leftover_controller.dart';

/// D-06 — "Còn dư món ăn?". Saves leftover portions as an "Ăn liền" batch with
/// a use-by reminder.
class LeftoverSaveSheet extends ConsumerStatefulWidget {
  const LeftoverSaveSheet({
    required this.dishId,
    required this.dishName,
    required this.initialServings,
    super.key,
  });

  final String dishId;
  final String dishName;
  final int initialServings;

  static Future<void> show(
    BuildContext context, {
    required String dishId,
    required String dishName,
    required int initialServings,
  }) =>
      showAppBottomSheet(
        context,
        builder: (_) => LeftoverSaveSheet(
          dishId: dishId,
          dishName: dishName,
          initialServings: initialServings < 1 ? 1 : initialServings,
        ),
      );

  @override
  ConsumerState<LeftoverSaveSheet> createState() => _State();
}

class _State extends ConsumerState<LeftoverSaveSheet> {
  late int _servings = widget.initialServings;
  int _reminderDays = 2;
  bool _busy = false;

  Future<void> _save() async {
    setState(() => _busy = true);
    try {
      await ref.read(leftoverControllerProvider.notifier).save(
            CookedFood(
              dishId: widget.dishId,
              dishName: widget.dishName,
              servings: _servings,
              reminderInDays: _reminderDays,
            ),
          );
      if (!mounted) return;
      Navigator.of(context).pop();
      AppSnack.show(context, 'Đã lưu phần thừa vào kho');
    } catch (_) {
      if (!mounted) return;
      setState(() => _busy = false);
      AppSnack.show(context, 'Không lưu được. Thử lại.');
    }
  }

  @override
  Widget build(BuildContext context) {
    return SheetBody(
      title: 'Còn dư món ăn?',
      subtitle: 'Lưu phần còn lại vào kho (tầng Ăn liền) và đặt nhắc dùng sớm.',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _Row(
            label: 'Số khẩu phần còn',
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconButton.filledTonal(
                  visualDensity: VisualDensity.compact,
                  onPressed: _servings > 1
                      ? () => setState(() => _servings--)
                      : null,
                  icon: const Icon(Icons.remove_rounded, size: 18),
                ),
                const SizedBox(width: Gap.sm),
                Text('$_servings phần', style: context.text.titleSmall),
                const SizedBox(width: Gap.sm),
                IconButton.filledTonal(
                  visualDensity: VisualDensity.compact,
                  onPressed: _servings < 12
                      ? () => setState(() => _servings++)
                      : null,
                  icon: const Icon(Icons.add_rounded, size: 18),
                ),
              ],
            ),
          ),
          Gap.gapSm,
          _Row(
            label: 'Nhắc dùng',
            child: DropdownButton<int>(
              value: _reminderDays,
              underline: const SizedBox.shrink(),
              onChanged: _busy
                  ? null
                  : (v) => setState(() => _reminderDays = v ?? 2),
              items: const [
                DropdownMenuItem(value: 1, child: Text('Sau 1 ngày')),
                DropdownMenuItem(value: 2, child: Text('Sau 2 ngày')),
                DropdownMenuItem(value: 3, child: Text('Sau 3 ngày')),
              ],
            ),
          ),
          Gap.gapSm,
          Container(
            padding: const EdgeInsets.all(Gap.sm),
            decoration: BoxDecoration(
              color: context.sweep.expired.bg,
              borderRadius: Radii.brMd,
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.info_outline_rounded,
                  size: 15,
                  color: context.sweep.expired.fg,
                ),
                const SizedBox(width: Gap.xs),
                Expanded(
                  child: Text(
                    'Thức ăn đã nấu nên dùng trong 1–2 ngày. Kiểm tra mùi và '
                    'trạng thái trước khi ăn.',
                    style: context.text.labelMedium?.copyWith(
                      color: context.sweep.expired.fg,
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Gap.gapMd,
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _busy ? null : () => Navigator.of(context).pop(),
                  child: const Text('Bỏ qua'),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: FilledButton(
                  onPressed: _busy ? null : _save,
                  child: _busy
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.4,
                            color: Colors.white,
                          ),
                        )
                      : const Text('Lưu phần thừa'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row({required this.label, required this.child});

  final String label;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Gap.sm, vertical: Gap.xs),
      decoration: BoxDecoration(
        borderRadius: Radii.brMd,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Row(
        children: [
          Expanded(child: Text(label, style: context.text.titleSmall)),
          child,
        ],
      ),
    );
  }
}
