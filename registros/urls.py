from django.urls import path
from . import views

app_name = 'registros'

urlpatterns = [
    path('nova/', views.nova_ocorrencia_view, name='nova_ocorrencia'),
    path('minhas/', views.minhas_ocorrencias_view, name='minhas_ocorrencias'),
]
