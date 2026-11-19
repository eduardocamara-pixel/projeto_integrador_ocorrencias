from django.db import models
from django.conf import settings


class TipoRegistroAcompanhamento(models.TextChoices):
    ORIENTACAO = 'ORIENTACAO', 'Conversa de Orientação com Estudante'
    REUNIAO_RESPONSAVEIS = 'REUNIAO_RESPONSAVEIS', 'Reunião com Pais / Responsáveis'
    TERMO_COMPROMISSO = 'TERMO_COMPROMISSO', 'Termo de Compromisso Pedagógico'
    ADVERTENCIA = 'ADVERTENCIA', 'Advertência Verbal ou Escrita'
    ENCAMINHAMENTO_EXTERNO = 'ENCAMINHAMENTO_EXTERNO', 'Encaminhamento Externo (Conselho Tutelar / Psicológico / Saúde)'
    OUTRO = 'OUTRO', 'Outras Providências Pedagógicas'


class Acompanhamento(models.Model):
    """
    Registro das intervenções pedagógicas e tramitações realizadas pela Coordenação Pedagógica.
    Permite registrar atas de reuniões, termos de compromisso e encaminhamentos.
    """
    ocorrencia = models.ForeignKey(
        'registros.Ocorrencia',
        on_delete=models.CASCADE,
        related_name='acompanhamentos',
        verbose_name='Ocorrência Vinculada'
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='acompanhamentos_realizados',
        verbose_name='Profissional Responsável'
    )
    tipo_registro = models.CharField(
        'Tipo de Registro Pedagógico',
        max_length=50,
        choices=TipoRegistroAcompanhamento.choices,
        default=TipoRegistroAcompanhamento.ORIENTACAO
    )
    observacao = models.TextField(
        'Observações Pedagógicas / Parecer',
        help_text='Relato detalhado da intervenção, diálogo ou reunião realizada.'
    )
    encaminhamento = models.TextField(
        'Encaminhamentos / Próximos Passos',
        blank=True,
        help_text='Ações combinadas, datas de retorno ou instituições contatadas.'
    )
    data_registro = models.DateTimeField(
        'Data de Registro',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Acompanhamento Pedagógico'
        verbose_name_plural = 'Acompanhamentos Pedagógicos'
        ordering = ['-data_registro']
        indexes = [
            models.Index(fields=['-data_registro'], name='acomp_dt_reg_idx'),
            models.Index(fields=['tipo_registro'], name='acomp_tipo_idx'),
        ]

    def __str__(self):
        return f"Acompanhamento #{self.id} - Ocorrência #{self.ocorrencia_id} ({self.get_tipo_registro_display()})"


class HistoricoAlteracao(models.Model):
    """
    Trilha de auditoria e conformidade LGPD.
    Registra qualquer alteração de status, despachos ou edições em uma ocorrência.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='historico_alteracoes',
        verbose_name='Usuário Responsável'
    )
    ocorrencia = models.ForeignKey(
        'registros.Ocorrencia',
        on_delete=models.CASCADE,
        related_name='historico_alteracoes',
        verbose_name='Ocorrência'
    )
    acao_realizada = models.CharField(
        'Ação Realizada',
        max_length=100,
        help_text='Exemplo: Criação, Mudança de Status para EM_ANALISE, Edição de Descrição.'
    )
    descricao_alteracao = models.TextField(
        'Descrição da Alteração',
        blank=True
    )
    data_hora = models.DateTimeField(
        'Data e Horário da Alteração',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Histórico de Alteração'
        verbose_name_plural = 'Histórico de Alterações'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['ocorrencia', '-data_hora'], name='hist_ocor_data_idx'),
        ]

    def __str__(self):
        return f"{self.data_hora.strftime('%d/%m/%Y %H:%M')} - {self.usuario.nome}: {self.acao_realizada}"
