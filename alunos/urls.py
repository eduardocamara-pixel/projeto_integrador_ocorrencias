from django.urls import path
from . import views

app_name = 'alunos'

urlpatterns = [
    path('', views.lista_alunos_view, name='lista_alunos'),
    path('cadastrar/', views.cadastrar_aluno_view, name='cadastrar_aluno'),
    path('<int:pk>/editar/', views.editar_aluno_view, name='editar_aluno'),
    path('<int:pk>/prontuario/', views.prontuario_aluno_view, name='prontuario_aluno'),
]
