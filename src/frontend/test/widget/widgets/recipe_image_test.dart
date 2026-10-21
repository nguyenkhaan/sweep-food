import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/widgets/recipe_image.dart';

class _FailingImageProvider extends ImageProvider<_FailingImageProvider> {
  const _FailingImageProvider();

  @override
  Future<_FailingImageProvider> obtainKey(ImageConfiguration configuration) {
    return SynchronousFuture<_FailingImageProvider>(this);
  }

  @override
  ImageStreamCompleter loadImage(
    _FailingImageProvider key,
    ImageDecoderCallback decode,
  ) {
    return OneFrameImageStreamCompleter(
      Future<ImageInfo>.error(Exception('Simulated image load error')),
    );
  }
}

void main() {
  Widget buildTestApp(Widget child) {
    return MaterialApp(
      theme: AppTheme.light,
      home: Scaffold(body: Center(child: child)),
    );
  }

  group('RecipeImage', () {
    testWidgets('null url renders restaurant placeholder icon', (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          const RecipeImage(imageUrl: null, width: 100, height: 100),
        ),
      );

      expect(find.byIcon(Icons.restaurant_rounded), findsOneWidget);
    });

    testWidgets('empty url renders restaurant placeholder icon', (
      tester,
    ) async {
      await tester.pumpWidget(
        buildTestApp(
          const RecipeImage(imageUrl: '   ', width: 100, height: 100),
        ),
      );

      expect(find.byIcon(Icons.restaurant_rounded), findsOneWidget);
    });

    testWidgets('failing image provider degrades gracefully to placeholder', (
      tester,
    ) async {
      await tester.pumpWidget(
        buildTestApp(
          const RecipeImage(
            imageProvider: _FailingImageProvider(),
            width: 100,
            height: 100,
          ),
        ),
      );
      await tester.pump();
      tester.takeException();

      expect(find.byIcon(Icons.restaurant_rounded), findsOneWidget);
    });

    testWidgets('failing remote url degrades gracefully to placeholder', (
      tester,
    ) async {
      await tester.pumpWidget(
        buildTestApp(
          const RecipeImage(
            imageUrl: 'https://cpcdn.com/failing_recipe.jpg',
            width: 100,
            height: 100,
          ),
        ),
      );
      await tester.pump();
      tester.takeException();

      expect(find.byIcon(Icons.restaurant_rounded), findsOneWidget);
    });
  });
}
