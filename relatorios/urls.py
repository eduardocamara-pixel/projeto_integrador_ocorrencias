from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('', views.painel_relatorios_view, name='painel'),
    path('geral/', views.relatorio_geral_view, name='relatorio_geral'),
    path('turma/<int:pk>/', views.relatorio_turma_view, name='relatorio_turma'),
    path('ocorrencia/<int:pk>/ficha/', views.ficha_ocorrencia_impressao_view, name='ficha_ocorrencia'),
]
