from django.urls import path
from . import views

app_name = 'registros'

urlpatterns = [
    path('nova/', views.nova_ocorrencia_view, name='nova_ocorrencia'),
    path('minhas/', views.minhas_ocorrencias_view, name='minhas_ocorrencias'),
    path('consulta/', views.consulta_ocorrencias_view, name='consulta_ocorrencias'),
    path('categorias/', views.lista_categorias_view, name='lista_categorias'),
    path('categorias/cadastrar/', views.cadastrar_categoria_view, name='cadastrar_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria_view, name='editar_categoria'),
    path('categorias/<int:pk>/toggle/', views.toggle_categoria_view, name='toggle_categoria'),
]
