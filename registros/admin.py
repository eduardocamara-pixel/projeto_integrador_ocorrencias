from django.contrib import admin
from .models import CategoriaOcorrencia, Ocorrencia


@admin.register(CategoriaOcorrencia)
class CategoriaOcorrenciaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_criacao')
    list_filter = ('ativo',)
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)


@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_aluno_nome',
        'get_turma_nome',
        'categoria',
        'professor',
        'data_ocorrencia',
        'status',
        'data_registro'
    )
    list_filter = (
        'status',
        'categoria',
        'matricula_turma__turma',
        'data_ocorrencia'
    )
    search_fields = (
        'matricula_turma__aluno__nome',
        'matricula_turma__aluno__matricula',
        'professor__nome',
        'descricao',
        'local'
    )
    autocomplete_fields = ('matricula_turma', 'professor', 'categoria')
    readonly_fields = ('data_registro', 'data_atualizacao')

    @admin.display(description='Aluno', ordering='matricula_turma__aluno__nome')
    def get_aluno_nome(self, obj):
        return obj.matricula_turma.aluno.nome

    @admin.display(description='Turma', ordering='matricula_turma__turma__nome')
    def get_turma_nome(self, obj):
        return obj.matricula_turma.turma.nome
