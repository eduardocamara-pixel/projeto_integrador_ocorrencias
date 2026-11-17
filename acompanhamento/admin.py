from django.contrib import admin
from .models import Acompanhamento, HistoricoAlteracao


@admin.register(Acompanhamento)
class AcompanhamentoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ocorrencia',
        'tipo_registro',
        'responsavel',
        'data_registro'
    )
    list_filter = ('tipo_registro', 'data_registro')
    search_fields = (
        'ocorrencia__matricula_turma__aluno__nome',
        'responsavel__nome',
        'observacao',
        'encaminhamento'
    )
    autocomplete_fields = ('ocorrencia', 'responsavel')
    readonly_fields = ('data_registro',)


@admin.register(HistoricoAlteracao)
class HistoricoAlteracaoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'data_hora',
        'usuario',
        'ocorrencia',
        'acao_realizada'
    )
    list_filter = ('data_hora', 'acao_realizada')
    search_fields = (
        'usuario__nome',
        'acao_realizada',
        'descricao_alteracao'
    )
    autocomplete_fields = ('usuario', 'ocorrencia')
    readonly_fields = ('data_hora',)
