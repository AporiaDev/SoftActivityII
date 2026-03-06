"""
Vistas API para el formulario de evaluación y el panel de administración.
"""
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Count

from .models import Question, Submission, Answer
from .serializers import (
    QuestionSerializer,
    SubmissionCreateSerializer,
    SubmissionResponseSerializer,
)


@api_view(['GET'])
@permission_classes([AllowAny])
def question_list(request):
    """Lista todas las preguntas (para el formulario del usuario)."""
    questions = Question.objects.all().order_by('order', 'id')
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def submission_create(request):
    """
    Recibe las respuestas, crea Submission + Answers, calcula el tipo resultante.
    Devuelve solo confirmación (sin resultados ni respuestas).
    """
    serializer = SubmissionCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    submission = serializer.save()
    return Response(
        {'message': 'Gracias por completar el formulario.', 'submission_id': submission.id},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_overview(request):
    """
    Métricas para el dashboard admin: total de envíos y distribución por tipo.
    """
    total = Submission.objects.count()
    by_type = (
        Submission.objects.filter(result_type__isnull=False)
        .values('result_type')
        .annotate(count=Count('id'))
        .order_by('result_type')
    )
    distribution = {r['result_type']: r['count'] for r in by_type}
    for t in ('a', 'b', 'c', 'd'):
        distribution.setdefault(t, 0)
    return Response({
        'total_submissions': total,
        'distribution': distribution,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_csv(request):
    """
    Exporta todas las respuestas con resultado: CSV (Excel-compatible).
    """
    submissions = Submission.objects.prefetch_related('answers__question').order_by('-created_at')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="evaluacion_respuestas.csv"'
    response.write('\ufeff')  # BOM para Excel en UTF-8
    lines = []
    lines.append('submission_id,fecha,resultado_tipo,pregunta_id,texto_pregunta,tipo_pregunta,valor')
    for sub in submissions:
        for ans in sub.answers.all():
            text_escaped = (ans.question.text or '').replace('"', '""')
            lines.append(
                f'{sub.id},{sub.created_at.strftime("%Y-%m-%d %H:%M")},{sub.result_type or ""},'
                f'{ans.question_id},"{text_escaped}",{ans.question.question_type},{ans.value}'
            )
    response.write('\r\n'.join(lines))
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_excel_view(request):
    """Exportar respuestas como .xlsx (requiere openpyxl)."""
    try:
        import openpyxl
        from openpyxl.writer.excel import save_virtual_workbook
    except ImportError:
        return HttpResponse('Se requiere openpyxl para exportar Excel.', status=501)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Respuestas'
    ws.append(['ID Envío', 'Fecha', 'Resultado tipo', 'Pregunta ID', 'Texto pregunta', 'Tipo pregunta', 'Valor'])
    for sub in Submission.objects.prefetch_related('answers__question').order_by('-created_at'):
        for ans in sub.answers.all():
            ws.append([
                sub.id,
                sub.created_at.strftime('%Y-%m-%d %H:%M'),
                sub.result_type or '',
                ans.question_id,
                ans.question.text or '',
                ans.question.question_type,
                ans.value,
            ])
    response = HttpResponse(
        save_virtual_workbook(wb),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="evaluacion_respuestas.xlsx"'
    return response
