"""
Vistas API para el formulario de evaluación y el panel de administración.
"""
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Count

from .models import Question, Submission, Answer, UserProfile
from .serializers import (
    QuestionSerializer,
    SubmissionCreateSerializer,
    SubmissionResponseSerializer,
)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf(request):
    """Devuelve el token CSRF para el cliente (login desde SPA)."""
    return Response({'csrfToken': get_token(request)})


def _normalize_cedula(cedula):
    """Cédula para búsqueda/almacenamiento: sin espacios y sin puntos ni guiones."""
    if not cedula:
        return ''
    s = str(cedula).strip().replace('.', '').replace('-', '').replace(' ', '')
    return s or str(cedula).strip()


@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """Registro con nombre, cédula y rol (responder encuesta o administrador)."""
    nombre = (request.data.get('nombre') or '').strip()
    cedula = _normalize_cedula(request.data.get('cedula') or '')
    rol = (request.data.get('rol') or request.data.get('role') or 'responder').strip().lower()
    if rol not in (UserProfile.ROL_RESPONDER, UserProfile.ROL_ADMIN):
        rol = UserProfile.ROL_RESPONDER
    if not nombre:
        return Response({'error': 'El nombre es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
    if not cedula:
        return Response({'error': 'La cédula es obligatoria'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=cedula).exists():
        return Response({'error': 'Ya existe un usuario registrado con esta cédula'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create(username=cedula, first_name=nombre)
    user.set_unusable_password()
    if rol == UserProfile.ROL_ADMIN:
        user.is_staff = True
    user.save()
    UserProfile.objects.create(user=user, role=rol)
    return Response({'message': 'Registro exitoso. Ya puede ingresar con su nombre y cédula.'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """Login con nombre y cédula (usuarios registrados). Staff puede acceder al dashboard."""
    nombre = (request.data.get('nombre') or '').strip()
    cedula = _normalize_cedula(request.data.get('cedula') or '')
    if not cedula:
        return Response({'error': 'La cédula es obligatoria'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(username=cedula)
    except User.DoesNotExist:
        return Response({'error': 'Nombre o cédula incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)
    nombre_ok = (user.first_name or '').strip().lower() == nombre.lower()
    if not nombre_ok:
        return Response({'error': 'Nombre o cédula incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)
    login(request, user)
    try:
        profile = user.evaluation_profile
        role = profile.role
    except UserProfile.DoesNotExist:
        role = UserProfile.ROL_RESPONDER
    return Response({
        'username': user.username,
        'nombre': user.first_name,
        'is_staff': user.is_staff,
        'rol': role,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """Cerrar sesión."""
    logout(request)
    return Response({'ok': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_me(request):
    """Indica si hay sesión activa (para rutas protegidas)."""
    try:
        profile = request.user.evaluation_profile
        role = profile.role
    except UserProfile.DoesNotExist:
        role = UserProfile.ROL_RESPONDER
    return Response({
        'username': request.user.username,
        'nombre': request.user.first_name or request.user.username,
        'is_staff': request.user.is_staff,
        'rol': role,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def question_list(request):
    """Lista todas las preguntas (para el formulario del usuario)."""
    questions = Question.objects.all().order_by('order', 'id')
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submission_create(request):
    """
    Recibe las respuestas, crea Submission + Answers (asociado al usuario logueado).
    Solo usuarios autenticados pueden enviar (quien responde la encuesta).
    """
    serializer = SubmissionCreateSerializer(data=request.data, context={'request': request})
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
    Métricas para el dashboard admin: total de envíos y distribución por tipo. Solo staff.
    """
    if not request.user.is_staff:
        return Response({'error': 'Sin permisos de administrador'}, status=status.HTTP_403_FORBIDDEN)
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
    Exporta todas las respuestas con resultado: CSV (Excel-compatible). Solo staff.
    """
    if not request.user.is_staff:
        return Response({'error': 'Sin permisos de administrador'}, status=status.HTTP_403_FORBIDDEN)
    submissions = Submission.objects.select_related('user').prefetch_related('answers__question').order_by('-created_at')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="evaluacion_respuestas.csv"'
    response.write('\ufeff')  # BOM para Excel en UTF-8
    lines = []
    lines.append('submission_id,fecha,resultado_tipo,usuario_nombre,usuario_cedula,pregunta_id,texto_pregunta,tipo_pregunta,valor')
    for sub in submissions:
        u = sub.user
        nombre = (u.first_name or '').replace('"', '""') if u else ''
        cedula = (u.username or '') if u else ''
        for ans in sub.answers.all():
            text_escaped = (ans.question.text or '').replace('"', '""')
            lines.append(
                f'{sub.id},{sub.created_at.strftime("%Y-%m-%d %H:%M")},{sub.result_type or ""},'
                f'"{nombre}",{cedula},{ans.question_id},"{text_escaped}",{ans.question.question_type},{ans.value}'
            )
    response.write('\r\n'.join(lines))
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_excel_view(request):
    """Exportar respuestas como .xlsx (requiere openpyxl). Solo staff."""
    if not request.user.is_staff:
        return Response({'error': 'Sin permisos de administrador'}, status=status.HTTP_403_FORBIDDEN)
    try:
        import openpyxl
        from openpyxl.writer.excel import save_virtual_workbook
    except ImportError:
        return HttpResponse('Se requiere openpyxl para exportar Excel.', status=501)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Respuestas'
    ws.append(['ID Envío', 'Fecha', 'Resultado tipo', 'Usuario nombre', 'Usuario cédula', 'Pregunta ID', 'Texto pregunta', 'Tipo pregunta', 'Valor'])
    for sub in Submission.objects.select_related('user').prefetch_related('answers__question').order_by('-created_at'):
        u = sub.user
        for ans in sub.answers.all():
            ws.append([
                sub.id,
                sub.created_at.strftime('%Y-%m-%d %H:%M'),
                sub.result_type or '',
                (u.first_name or '') if u else '',
                (u.username or '') if u else '',
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
