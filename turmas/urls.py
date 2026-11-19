from django.urls import path
from . import views

app_name = 'turmas'

urlpatterns = [
    path('', views.lista_turmas_view, name='lista_turmas'),
    path('cadastrar/', views.cadastrar_turma_view, name='cadastrar_turma'),
    path('<int:pk>/', views.detalhe_turma_view, name='detalhe_turma'),
    path('<int:pk>/editar/', views.editar_turma_view, name='editar_turma'),
    path('<int:pk>/matricular/', views.matricular_aluno_view, name='matricular_aluno'),
]
