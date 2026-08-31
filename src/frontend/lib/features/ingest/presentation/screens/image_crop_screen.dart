// lib/features/ingest/presentation/screens/image_crop_screen.dart
// I-02 Cắt / chỉnh ảnh

import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_colors.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:go_router/go_router.dart';

/// I-02 — Màn hình cắt / căn chỉnh ảnh trước khi gửi OCR.
class ImageCropScreen extends StatelessWidget {
  const ImageCropScreen({
    this.imagePath,
    super.key,
  });

  final String? imagePath;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0D0B),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        foregroundColor: Colors.white,
        leading: IconButton(
          onPressed: () => context.pop(),
          icon: const Icon(Icons.close_rounded),
        ),
        title: const Text('Căn chỉnh ảnh'),
        actions: [
          TextButton(
            onPressed: () => context.pop(imagePath),
            child: Text(
              'Xong',
              style: context.text.titleSmall?.copyWith(
                color: BrandPalette.green300,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: Center(
                child: Container(
                  margin: const EdgeInsets.all(Gap.lg),
                  decoration: BoxDecoration(
                    color: Colors.white10,
                    borderRadius: Radii.brLg,
                    border: Border.all(color: BrandPalette.green300, width: 2),
                  ),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.crop_rounded,
                          size: 48,
                          color: BrandPalette.green300,
                        ),
                        const SizedBox(height: Gap.md),
                        Text(
                          'Kéo các góc để căn chỉnh nhãn',
                          style: context.text.bodyMedium?.copyWith(
                            color: Colors.white70,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(Gap.lg),
              child: ElevatedButton(
                onPressed: () => context.pop(imagePath),
                style: ElevatedButton.styleFrom(
                  backgroundColor: BrandPalette.green700,
                  foregroundColor: Colors.white,
                  minimumSize: const Size.fromHeight(50),
                  shape: const RoundedRectangleBorder(
                    borderRadius: Radii.brMd,
                  ),
                ),
                child: const Text('Tiếp tục'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
