from django.contrib import admin
from .models import Turma, MatriculaTurma


class MatriculaTurmaInline(admin.TabularInline):
    model = MatriculaTurma
    extra = 1
    autocomplete_fields = ('aluno',)


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'serie', 'turno', 'ano_letivo', 'ativa', 'data_criacao')
    list_filter = ('ano_letivo', 'turno', 'ativa', 'serie')
    search_fields = ('nome', 'serie')
    ordering = ('-ano_letivo', 'nome')
    inlines = [MatriculaTurmaInline]


@admin.register(MatriculaTurma)
class MatriculaTurmaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'situacao', 'data_entrada', 'data_saida')
    list_filter = ('situacao', 'turma__ano_letivo', 'turma')
    search_fields = ('aluno__nome', 'aluno__matricula', 'turma__nome')
    autocomplete_fields = ('aluno', 'turma')
