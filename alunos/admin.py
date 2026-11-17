from django.contrib import admin
from .models import Aluno


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nome', 'data_nascimento', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'data_nascimento')
    search_fields = ('matricula', 'nome')
    ordering = ('nome',)
    readonly_fields = ('data_criacao', 'data_atualizacao')
