"""
Serializers para la API de evaluación.
"""
from rest_framework import serializers
from .models import Question, Submission, Answer


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'order']


class AnswerInputSerializer(serializers.Serializer):
    """Payload: { "question_id": int, "value": int (1-10) }"""
    question_id = serializers.IntegerField(min_value=1)
    value = serializers.IntegerField(min_value=1, max_value=10)


class SubmissionCreateSerializer(serializers.Serializer):
    """Payload: { "answers": [ { "question_id": 1, "value": 5 }, ... ] }"""
    answers = serializers.ListField(child=AnswerInputSerializer(), allow_empty=False)

    def validate_answers(self, value):
        question_ids = [a['question_id'] for a in value]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError('No puede haber respuestas duplicadas para la misma pregunta.')
        existing = set(Question.objects.filter(id__in=question_ids).values_list('id', flat=True))
        missing = set(question_ids) - existing
        if missing:
            raise serializers.ValidationError(f'Preguntas no encontradas: {sorted(missing)}')
        return value

    def create(self, validated_data):
        user = self.context.get('request').user if self.context.get('request') else None
        submission = Submission.objects.create(user=user if (user and user.is_authenticated) else None)
        answers_data = validated_data['answers']
        question_ids = [a['question_id'] for a in answers_data]
        questions = {q.id: q for q in Question.objects.filter(id__in=question_ids)}
        for item in answers_data:
            Answer.objects.create(
                submission=submission,
                question=questions[item['question_id']],
                value=item['value']
            )
        submission.recalculate_result()
        return submission


class SubmissionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'created_at']


class AnswerExportSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)

    class Meta:
        model = Answer
        fields = ['question_id', 'question_text', 'question_type', 'value']
