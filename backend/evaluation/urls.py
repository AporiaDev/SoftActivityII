"""
URLs de la API de evaluación.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('questions/', views.question_list),
    path('submit/', views.submission_create),
    path('stats/', views.stats_overview),
    path('export/csv/', views.export_csv),
    path('export/xlsx/', views.export_excel_view),
]
