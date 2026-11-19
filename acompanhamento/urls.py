from django.urls import path
from . import views

app_name = 'acompanhamento'

urlpatterns = [
    path('triagem/', views.painel_triagem_view, name='triagem'),
    path('ocorrencia/<int:pk>/', views.detalhe_triagem_view, name='detalhe_ocorrencia'),
    path('triagem/<int:pk>/', views.detalhe_triagem_view, name='detalhe_triagem'),
]
