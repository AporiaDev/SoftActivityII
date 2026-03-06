"""
Modelos para la evaluación de perfiles/personalidad.
"""
from django.db import models
from django.conf import settings


def scale_value_to_level(value):
    """
    Convierte el valor de la escala visual (1-10) al nivel de puntuación (1-5).
    - 1 o 2  → 1 punto
    - 3 o 4  → 2 puntos
    - 5 o 6  → 3 puntos
    - 7 u 8  → 4 puntos
    - 9 o 10 → 5 puntos
    """
    if value is None:
        return 0
    value = int(value)
    if value <= 2:
        return 1
    if value <= 4:
        return 2
    if value <= 6:
        return 3
    if value <= 8:
        return 4
    return 5


def calculate_profile_type(answers_queryset):
    """
    Dado un queryset de Answer (de una misma Submission), suma los puntos
    por tipo (usando el tipo de cada Question) y devuelve el tipo con mayor suma.
    answers_queryset: Answer.objects.filter(submission=submission).select_related('question')
    """
    totals = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
    for answer in answers_queryset:
        level = scale_value_to_level(answer.value)
        q_type = answer.question.question_type
        if q_type in totals:
            totals[q_type] += level
    if not any(totals.values()):
        return None
    return max(totals, key=totals.get)


class UserProfile(models.Model):
    """Perfil del usuario: rol elegido al registrarse (responder encuesta o administrador)."""
    ROL_RESPONDER = 'responder'
    ROL_ADMIN = 'admin'
    ROLES = [(ROL_RESPONDER, 'Responder encuesta'), (ROL_ADMIN, 'Administrador')]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluation_profile',
        primary_key=True,
    )
    role = models.CharField(max_length=20, choices=ROLES, default=ROL_RESPONDER, db_index=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'


class Question(models.Model):
    """Pregunta del formulario con su tipo asociado (a, b, c, d)."""
    QUESTION_TYPES = [
        ('a', 'Tipo A'),
        ('b', 'Tipo B'),
        ('c', 'Tipo C'),
        ('d', 'Tipo D'),
    ]
    text = models.TextField(verbose_name='Texto de la pregunta')
    question_type = models.CharField(
        max_length=1,
        choices=QUESTION_TYPES,
        db_index=True,
        verbose_name='Tipo/Categoría'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'

    def __str__(self):
        return self.text[:60] + '...' if len(self.text) > 60 else self.text


class Submission(models.Model):
    """Envío del formulario: fecha, usuario (quien responde) y resultado calculado (tipo de perfil)."""
    PROFILE_TYPES = [
        ('a', 'Tipo A'),
        ('b', 'Tipo B'),
        ('c', 'Tipo C'),
        ('d', 'Tipo D'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluation_submissions',
        verbose_name='Usuario que respondió'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    result_type = models.CharField(
        max_length=1,
        choices=PROFILE_TYPES,
        null=True,
        blank=True,
        db_index=True,
        verbose_name='Tipo de perfil resultante'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Envío'
        verbose_name_plural = 'Envíos'

    def __str__(self):
        return f"Envío {self.id} - {self.created_at.date()} ({self.result_type or 'N/A'})"

    def recalculate_result(self):
        """Recalcula result_type a partir de las respuestas asociadas."""
        answers = self.answers.select_related('question').all()
        self.result_type = calculate_profile_type(answers)
        self.save(update_fields=['result_type'])


class Answer(models.Model):
    """Respuesta: valor (1-10) a una pregunta dentro de un envío."""
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Envío'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Pregunta'
    )
    value = models.PositiveSmallIntegerField(
        verbose_name='Valor (1-10)',
        help_text='Valor seleccionado en la escala del 1 al 10'
    )

    class Meta:
        unique_together = [['submission', 'question']]
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'

    def __str__(self):
        return f"P{self.question_id} = {self.value} (envío {self.submission_id})"
