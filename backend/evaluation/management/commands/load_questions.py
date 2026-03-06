"""
Comando de management para precargar las preguntas del formulario (seed).
Uso: python manage.py load_questions
"""
import json
from django.core.management.base import BaseCommand
from evaluation.models import Question


QUESTIONS_DATA = [
    {"text": "Generalmente no me acerco a los problemas en forma creativa", "type": "c"},
    {"text": "Me gusta probar y luego revisar mis ideas antes de generar la solucion o el producto final", "type": "c"},
    {"text": "Me gusta tomarme el tiempo para clarificar la naturaleza exacta del problema", "type": "a"},
    {"text": "Disfruto de tomar los pasos necesarios para poner mis ideas en acción", "type": "d"},
    {"text": "Me gusta separar un problema amplio en partes para examinarlo desde todos los angulos", "type": "c"},
    {"text": "Tengo dificultad en tener ideas inusuales para resolver un problema", "type": "b"},
    {"text": "Me gusta identificar los hechos más relevantes relativos al problema", "type": "a"},
    {"text": "No tengo el temperamento para tratar de aislar las causas especificas de un problema", "type": "a"},
    {"text": "Disfruto al generar formas únicas de mirar un problema", "type": "b"},
    {"text": "Me gusta generar todos los pros y los contras de una solución potencial", "type": "c"},
    {"text": "Antes de implemetar una solución me gusta separarla en pasos", "type": "c"},
    {"text": "Transformar ideas en acción no es lo que disfruto más", "type": "d"},
    {"text": "Me gusta superar el criterio que puede usarse para identificar la mejor opcion o solución", "type": "c"},
    {"text": "Disfruto de pasar tiempo profundizando en el analisis inicial del problema", "type": "b"},
    {"text": "Por naturaleza no paso mucho tiempo en definir el problema exacto a resolver", "type": "a"},
    {"text": "Disfruto de usar mi imaginación para producir muchas ideas", "type": "b"},
    {"text": "Me gusta enfocarme en la información clave de una situación desafiante", "type": "a"},
    {"text": "Disfruto de tomarme el tiempo para perfeccionar una idea", "type": "c"},
    {"text": "Me resulta dificil implementar mis ideas", "type": "d"},
    {"text": "Disfruto de transformar ideas en bruto en soluciones concretas", "type": "d"},
    {"text": "No paso el tiempo en todas las cosas que necesito hacer para implementar una idea", "type": "d"},
    {"text": "Realmente disfruto de implementar una idea", "type": "d"},
    {"text": "Antes de avanzar me gusta tener una clara comprensión del problema", "type": "a"},
    {"text": "Me gusta trabajar con ideas únicas", "type": "b"},
    {"text": "Disfruto de poner mis ideas en acción", "type": "d"},
    {"text": "Me gusta explorar las fortalezas y debilidades de una solución potencial", "type": "c"},
    {"text": "Disfruto de reunir información para identificar el origen de un problema en particular", "type": "a"},
    {"text": "Disfruto del analisis y el esfuerzo que llevo a transformar un concepto preliminar en una idea factible", "type": "c"},
    {"text": "Mi tendencia natural no es generar muchas ideas para los problemas", "type": "b"},
    {"text": "Encuentro que tengo poca paciencia para el esfuerzo que lleva a pulir o refinar una idea", "type": "b"},
    {"text": "Tiendo a buscar una solución rapida y luego implementarla", "type": "c"},
]


class Command(BaseCommand):
    help = 'Carga las preguntas del formulario de evaluación (seed). Crea o actualiza por orden.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar todas las preguntas existentes antes de cargar.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted, _ = Question.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Eliminadas {deleted} preguntas.'))

        created = 0
        updated = 0
        for order, item in enumerate(QUESTIONS_DATA, start=1):
            text = item['text']
            qtype = item['type'].lower()
            if qtype not in ('a', 'b', 'c', 'd'):
                self.stdout.write(self.style.WARNING(f"Tipo '{qtype}' ignorado en: {text[:50]}..."))
                continue
            obj, was_created = Question.objects.update_or_create(
                id=order,
                defaults={
                    'text': text,
                    'question_type': qtype,
                    'order': order,
                }
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seed completado: {created} creadas, {updated} actualizadas. Total: {Question.objects.count()} preguntas.'
        ))
