class FreshnessQuestionOptionDto {
  const FreshnessQuestionOptionDto({
    required this.value,
    required this.labelVi,
  });

  final String value;
  final String labelVi;

  factory FreshnessQuestionOptionDto.fromJson(Map<String, dynamic> json) =>
      FreshnessQuestionOptionDto(
        value: json['value'] as String,
        labelVi: json['label_vi'] as String,
      );
}

class FreshnessQuestionDto {
  const FreshnessQuestionDto({
    required this.axis,
    required this.questionVi,
    required this.options,
    required this.defaultValue,
  });

  final String axis;
  final String questionVi;
  final List<FreshnessQuestionOptionDto> options;
  final String defaultValue;

  factory FreshnessQuestionDto.fromJson(Map<String, dynamic> json) =>
      FreshnessQuestionDto(
        axis: json['axis'] as String,
        questionVi: json['question_vi'] as String,
        options: (json['options'] as List<dynamic>)
            .map((e) =>
                FreshnessQuestionOptionDto.fromJson(e as Map<String, dynamic>))
            .toList(),
        defaultValue: (json['default'] ?? '') as String,
      );
}

class FreshnessQuestionsResponseDto {
  const FreshnessQuestionsResponseDto({
    required this.kbVersion,
    required this.freshcheckIngredientId,
    required this.archetypeId,
    required this.questions,
  });

  final String kbVersion;
  final String freshcheckIngredientId;
  final String archetypeId;
  final List<FreshnessQuestionDto> questions;

  factory FreshnessQuestionsResponseDto.fromJson(Map<String, dynamic> json) =>
      FreshnessQuestionsResponseDto(
        kbVersion: json['kb_version'] as String? ?? '',
        freshcheckIngredientId:
            json['freshcheck_ingredient_id'] as String? ?? '',
        archetypeId: json['archetype_id'] as String? ?? '',
        questions: (json['questions'] as List<dynamic>? ?? [])
            .map((e) => FreshnessQuestionDto.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

class FreshnessAssessmentResponseDto {
  const FreshnessAssessmentResponseDto({
    required this.assessmentId,
    required this.batchId,
    required this.blocked,
    this.tier,
    this.score,
    this.remainingDaysMin,
    this.remainingDaysMax,
    required this.reasonsVi,
    required this.storageTipsVi,
    this.expiresAt,
  });

  final String assessmentId;
  final String batchId;
  final bool blocked;
  final String? tier;
  final double? score;
  final int? remainingDaysMin;
  final int? remainingDaysMax;
  final List<String> reasonsVi;
  final List<String> storageTipsVi;
  final DateTime? expiresAt;

  factory FreshnessAssessmentResponseDto.fromJson(Map<String, dynamic> json) =>
      FreshnessAssessmentResponseDto(
        assessmentId: json['assessment_id'] as String? ?? '',
        batchId: json['batch_id'] as String? ?? '',
        blocked: json['blocked'] as bool? ?? false,
        tier: json['tier'] as String?,
        score: (json['score'] as num?)?.toDouble(),
        remainingDaysMin: json['remaining_days_min'] as int?,
        remainingDaysMax: json['remaining_days_max'] as int?,
        reasonsVi: (json['reasons_vi'] as List<dynamic>? ?? [])
            .map((e) => e.toString())
            .toList(),
        storageTipsVi: (json['storage_tips_vi'] as List<dynamic>? ?? [])
            .map((e) => e.toString())
            .toList(),
        expiresAt: json['expires_at'] != null
            ? DateTime.tryParse(json['expires_at'].toString())
            : null,
      );
}
