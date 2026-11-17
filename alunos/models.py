from django.db import models


class Aluno(models.Model):
    """
    Entidade Aluno no SIGOE.
    Armazena os dados cadastrais básicos e de identificação acadêmica do estudante.
    """
    nome = models.CharField(
        'Nome Completo',
        max_length=150
    )
    matricula = models.CharField(
        'Matrícula',
        max_length=50,
        unique=True,
        help_text='Código identificador único do estudante na instituição escolar.'
    )
    data_nascimento = models.DateField(
        'Data de Nascimento',
        help_text='Utilizada para acompanhamento pedagógico e proteção de menores (LGPD).'
    )
    ativo = models.BooleanField(
        'Ativo',
        default=True,
        help_text='Indica se o aluno possui vínculo ativo com a instituição.'
    )
    data_criacao = models.DateTimeField(
        'Data de Cadastro',
        auto_now_add=True
    )
    data_atualizacao = models.DateTimeField(
        'Última Atualização',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['nome']

    def __str__(self):
        return f"{self.matricula} - {self.nome}"
