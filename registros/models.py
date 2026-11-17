from django.db import models
from django.conf import settings
from django.utils import timezone


class StatusOcorrencia(models.TextChoices):
    REGISTRADA = 'REGISTRADA', 'Registrada'
    EM_ANALISE = 'EM_ANALISE', 'Em Análise'
    EM_ACOMPANHAMENTO = 'EM_ACOMPANHAMENTO', 'Em Acompanhamento'
    ENCAMINHADA = 'ENCAMINHADA', 'Encaminhada'
    CONCLUIDA = 'CONCLUIDA', 'Concluída'


class CategoriaOcorrencia(models.Model):
    """
    Classificação configurável de ocorrências escolares.
    Exemplos: Indisciplina, Conflitos entre estudantes, Danos ao patrimônio, etc.
    """
    nome = models.CharField(
        'Nome da Categoria',
        max_length=100,
        unique=True
    )
    descricao = models.TextField(
        'Descrição',
        blank=True
    )
    ativo = models.BooleanField(
        'Ativo',
        default=True,
        help_text='Indica se a categoria está disponível para seleção.'
    )
    data_criacao = models.DateTimeField(
        'Data de Criação',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Categoria de Ocorrência'
        verbose_name_plural = 'Categorias de Ocorrências'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Ocorrencia(models.Model):
    """
    Registro formal de ocorrência disciplinar ou comportamental.
    Vincula o estudante (no contexto da sua turma e matrícula), o professor autor, a categoria e os fatos.
    """
    matricula_turma = models.ForeignKey(
        'turmas.MatriculaTurma',
        on_delete=models.PROTECT,
        related_name='ocorrencias',
        verbose_name='Estudante (Matrícula/Turma)'
    )
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ocorrencias_registradas',
        verbose_name='Professor Relator'
    )
    categoria = models.ForeignKey(
        CategoriaOcorrencia,
        on_delete=models.PROTECT,
        related_name='ocorrencias',
        verbose_name='Categoria'
    )
    data_ocorrencia = models.DateTimeField(
        'Data e Horário do Fato',
        default=timezone.now
    )
    data_registro = models.DateTimeField(
        'Data de Registro no Sistema',
        auto_now_add=True
    )
    local = models.CharField(
        'Local do Fato',
        max_length=150,
        help_text='Exemplo: Sala 12, Pátio, Refeitório, Quadra poliesportiva.'
    )
    descricao = models.TextField(
        'Descrição Detalhada do Fato',
        help_text='Relato fático, objetivo e descritivo, sem juízos de valor.'
    )
    providencias_iniciais = models.TextField(
        'Providências Iniciais Adotadas',
        blank=True,
        help_text='Ações imediatas adotadas pelo professor no momento do evento.'
    )
    status = models.CharField(
        'Status do Ciclo de Vida',
        max_length=25,
        choices=StatusOcorrencia.choices,
        default=StatusOcorrencia.REGISTRADA
    )
    data_atualizacao = models.DateTimeField(
        'Última Atualização',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Ocorrência'
        verbose_name_plural = 'Ocorrências'
        ordering = ['-data_ocorrencia', '-data_registro']

    def __str__(self):
        return f"Ocorrência #{self.id} - {self.matricula_turma.aluno.nome} ({self.get_status_display()})"

    @property
    def aluno(self):
        return self.matricula_turma.aluno

    @property
    def turma(self):
        return self.matricula_turma.turma
