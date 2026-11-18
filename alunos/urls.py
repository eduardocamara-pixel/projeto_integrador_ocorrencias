from django.urls import path
from . import views

app_name = 'alunos'

urlpatterns = [
    path('', views.lista_alunos_view, name='lista_alunos'),
    path('<int:pk>/prontuario/', views.prontuario_aluno_view, name='prontuario_aluno'),
]
