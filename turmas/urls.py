from django.urls import path
from . import views

app_name = 'turmas'

urlpatterns = [
    path('', views.lista_turmas_view, name='lista_turmas'),
    path('<int:pk>/', views.detalhe_turma_view, name='detalhe_turma'),
]
