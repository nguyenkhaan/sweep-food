// lib/core/permissions/permission_prime_sheet.dart
// G-04 — Bottom sheet xin quyền trước khi gọi prompt hệ thống
// Design: PermissionPrime.dc.html

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/permissions/permission_service.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:go_router/go_router.dart';

enum PermissionKind { camera, microphone }

/// G-04 gate: returns `true` only once the OS permission for [kind] is granted.
///
/// If not already granted it primes the user with [PermissionPrimeSheet] first
/// (so the system dialog never appears cold), then requests. A permanently
/// denied permission surfaces a "mở Cài đặt" snackbar and returns `false`.
Future<bool> ensureMediaPermission(
  BuildContext context,
  WidgetRef ref,
  PermissionKind kind,
) async {
  final service = ref.read(permissionServiceProvider);
  final isCamera = kind == PermissionKind.camera;

  if (isCamera
      ? await service.hasCameraPermission()
      : await service.hasMicrophonePermission()) {
    return true;
  }

  if (!context.mounted) return false;
  final primed = await showPermissionPrimeSheet(context, kind: kind);
  if (primed != true) return false;

  final granted = isCamera
      ? await service.requestCameraPermission()
      : await service.requestMicrophonePermission();
  if (granted) return true;

  final permanently = isCamera
      ? await service.isCameraPermanentlyDenied()
      : await service.isMicrophonePermanentlyDenied();
  if (context.mounted) {
    ScaffoldMessenger.of(context).showSnackBar(
      permanently
          ? SnackBar(
              content: Text(
                isCamera
                    ? 'Hãy bật quyền Máy ảnh trong Cài đặt để quét.'
                    : 'Hãy bật quyền Micro trong Cài đặt để nói.',
              ),
              action: SnackBarAction(
                label: 'Mở Cài đặt',
                onPressed: service.openSettings,
              ),
            )
          : SnackBar(
              content: Text(
                isCamera
                    ? 'Chưa cấp quyền Máy ảnh — hãy thử lại và chọn "Cho phép".'
                    : 'Chưa cấp quyền Micro — hãy thử lại và chọn "Cho phép".',
              ),
            ),
    );
  }
  return false;
}

/// Convenience helper to open the priming bottom sheet G-04.
/// Returns `true` if user tapped "Cho phép", `false`/`null` if dismissed.
Future<bool?> showPermissionPrimeSheet(
  BuildContext context, {
  required PermissionKind kind,
}) {
  return showModalBottomSheet<bool>(
    context: context,
    isScrollControlled: true,
    useSafeArea: true,
    backgroundColor: Colors.transparent,
    builder: (_) => PermissionPrimeSheet(kind: kind),
  );
}

/// G-04 — Sheet giải thích quyền trước khi mở dialog hệ thống.
class PermissionPrimeSheet extends StatelessWidget {
  const PermissionPrimeSheet({
    required this.kind,
    super.key,
  });

  final PermissionKind kind;

  @override
  Widget build(BuildContext context) {
    final cs = context.colors;
    final sweep = context.sweep;

    final isCamera = kind == PermissionKind.camera;
    final title = isCamera ? 'Cho phép dùng máy ảnh' : 'Cho phép dùng micro';
    final description = isCamera
        ? 'SweepFood cần máy ảnh để quét tem nhãn và hóa đơn. Ảnh chỉ dùng để trích xuất thông tin nguyên liệu, không lưu lại nếu bạn không xác nhận.'
        : 'SweepFood cần micro để nhận diện giọng nói khi bạn đọc danh sách nguyên liệu. Âm thanh chỉ được xử lý để bóc tách thông tin.';
    final iconData = isCamera ? Icons.camera_alt_outlined : Icons.mic_outlined;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: Radii.brSheet,
        boxShadow: Shadows.e3,
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.sm, Gap.lg, Gap.xl),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Grab handle
              Center(
                child: Container(
                  width: 38,
                  height: 4,
                  decoration: BoxDecoration(
                    color: sweep.hairline,
                    borderRadius: Radii.brSheet,
                  ),
                ),
              ),
              Gap.gapMd,

              // Icon badge
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: BrandPalette.green100,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Icon(
                  iconData,
                  size: 30,
                  color: BrandPalette.green700,
                ),
              ),
              Gap.gapMd,

              // Title
              Text(
                title,
                textAlign: TextAlign.center,
                style: context.text.titleLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              Gap.gapXs,

              // Description
              Text(
                description,
                textAlign: TextAlign.center,
                style: context.text.bodyMedium?.copyWith(
                  color: sweep.textSecondary,
                  height: 1.55,
                ),
              ),
              Gap.gapLg,

              // Buttons
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  ElevatedButton(
                    onPressed: () => context.pop(true),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: BrandPalette.green700,
                      foregroundColor: Colors.white,
                      minimumSize: const Size.fromHeight(48),
                      shape: const RoundedRectangleBorder(
                        borderRadius: Radii.brMd,
                      ),
                    ),
                    child: const Text('Cho phép'),
                  ),
                  Gap.gapXs,
                  TextButton(
                    onPressed: () => context.pop(false),
                    style: TextButton.styleFrom(
                      foregroundColor: sweep.textSecondary,
                      minimumSize: const Size.fromHeight(48),
                    ),
                    child: const Text('Không phải bây giờ'),
                  ),
                ],
              ),
              Gap.gapXs,

              // Fine print
              Text(
                'Bạn có thể đổi trong Cài đặt bất cứ lúc nào.',
                style: context.text.labelSmall?.copyWith(
                  color: sweep.textTertiary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
