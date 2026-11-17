from django.db import models
from django.utils import timezone


class TurnoTurma(models.TextChoices):
    MATUTINO = 'MATUTINO', 'Matutino'
    VESPERTINO = 'VESPERTINO', 'Vespertino'
    NOTURNO = 'NOTURNO', 'Noturno'
    INTEGRAL = 'INTEGRAL', 'Integral'


class SituacaoMatricula(models.TextChoices):
    ATIVA = 'ATIVA', 'Ativa'
    TRANSFERIDO = 'TRANSFERIDO', 'Transferido'
    CONCLUIDO = 'CONCLUIDO', 'Concluído'
    CANCELADO = 'CANCELADO', 'Cancelado'


class Turma(models.Model):
    """
    Entidade Turma no SIGOE.
    Agrupa estudantes em um determinado ano letivo, série e turno.
    """
    nome = models.CharField(
        'Nome da Turma',
        max_length=100,
        help_text='Exemplo: 9º Ano A, 3º Ano Informática'
    )
    serie = models.CharField(
        'Série / Etapa',
        max_length=50,
        help_text='Exemplo: 9º Ano Ensino Fundamental, 3º Médio'
    )
    turno = models.CharField(
        'Turno',
        max_length=20,
        choices=TurnoTurma.choices,
        default=TurnoTurma.MATUTINO
    )
    ano_letivo = models.PositiveIntegerField(
        'Ano Letivo',
        help_text='Exemplo: 2026'
    )
    ativa = models.BooleanField(
        'Ativa',
        default=True,
        help_text='Indica se a turma está em andamento.'
    )
    data_criacao = models.DateTimeField(
        'Data de Cadastro',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering = ['-ano_letivo', 'nome']
        unique_together = ('nome', 'ano_letivo')

    def __str__(self):
        return f"{self.nome} ({self.ano_letivo})"


class MatriculaTurma(models.Model):
    """
    Tabela associativa entre Aluno e Turma com histórico temporal.
    Permite registrar movimentações como transferências e conclusões.
    """
    aluno = models.ForeignKey(
        'alunos.Aluno',
        on_delete=models.CASCADE,
        related_name='matriculas',
        verbose_name='Aluno'
    )
    turma = models.ForeignKey(
        'turmas.Turma',
        on_delete=models.CASCADE,
        related_name='matriculas',
        verbose_name='Turma'
    )
    data_entrada = models.DateField(
        'Data de Entrada',
        default=timezone.localdate
    )
    data_saida = models.DateField(
        'Data de Saída',
        null=True,
        blank=True,
        help_text='Preenchido em caso de transferência, cancelamento ou conclusão.'
    )
    situacao = models.CharField(
        'Situação',
        max_length=20,
        choices=SituacaoMatricula.choices,
        default=SituacaoMatricula.ATIVA
    )

    class Meta:
        verbose_name = 'Matrícula em Turma'
        verbose_name_plural = 'Matrículas em Turmas'
        ordering = ['-data_entrada', 'aluno__nome']
        unique_together = ('aluno', 'turma', 'situacao')

    def __str__(self):
        return f"{self.aluno.nome} - {self.turma.nome} ({self.get_situacao_display()})"
