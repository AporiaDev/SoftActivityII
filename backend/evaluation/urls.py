"""
URLs de la API de evaluación.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('csrf/', views.get_csrf),
    path('register/', views.api_register),
    path('login/', views.api_login),
    path('logout/', views.api_logout),
    path('me/', views.api_me),
    path('questions/', views.question_list),
    path('submit/', views.submission_create),
    path('stats/', views.stats_overview),
    path('export/csv/', views.export_csv),
    path('export/xlsx/', views.export_excel_view),
]
