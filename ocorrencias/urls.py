from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('ocorrencias/', include('registros.urls')),
    path('turmas/', include('turmas.urls')),
    path('acompanhamento/', include('acompanhamento.urls')),
    path('alunos/', include('alunos.urls')),
    path('relatorios/', include('relatorios.urls')),
    path('', include('core.urls')),
]
