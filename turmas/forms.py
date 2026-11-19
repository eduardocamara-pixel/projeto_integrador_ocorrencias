from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Turma, MatriculaTurma, TurnoTurma, SituacaoMatricula
from alunos.models import Aluno


class TurmaForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de Turmas escolares.
    """
    class Meta:
        model = Turma
        fields = ['nome', 'serie', 'turno', 'ano_letivo', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 9º Ano A, 3º Ano Informática',
                'autofocus': True
            }),
            'serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 9º Ano Ensino Fundamental, 3º Médio'
            }),
            'turno': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ano_letivo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000,
                'max': 2100,
                'placeholder': 'Ex: 2026'
            }),
            'ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        ano_letivo = cleaned_data.get('ano_letivo')

        if nome and ano_letivo:
            qs = Turma.objects.filter(nome__iexact=nome, ano_letivo=ano_letivo)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(f"Já existe uma turma cadastrada com o nome '{nome}' para o ano letivo {ano_letivo}.")
        return cleaned_data


class MatriculaTurmaForm(forms.ModelForm):
    """
    Formulário para enturmar (matricular) um estudante em uma turma.
    """
    data_entrada = forms.DateField(
        label='Data de Ingresso na Turma',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        initial=date.today
    )

    class Meta:
        model = MatriculaTurma
        fields = ['aluno', 'data_entrada', 'situacao']
        widgets = {
            'aluno': forms.Select(attrs={
                'class': 'form-select select2-aluno'
            }),
            'situacao': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        turma = kwargs.pop('turma', None)
        super().__init__(*args, **kwargs)
        self.turma = turma
        # Filtrar discentes ativos
        self.fields['aluno'].queryset = Aluno.objects.filter(ativo=True).order_by('nome')

    def clean(self):
        cleaned_data = super().clean()
        aluno = cleaned_data.get('aluno')
        situacao = cleaned_data.get('situacao')

        if aluno and self.turma and situacao == SituacaoMatricula.ATIVA:
            # Verifica se já está matriculado ativamente nesta turma
            ja_matriculado = MatriculaTurma.objects.filter(
                aluno=aluno,
                turma=self.turma,
                situacao=SituacaoMatricula.ATIVA
            )
            if self.instance.pk:
                ja_matriculado = ja_matriculado.exclude(pk=self.instance.pk)
            if ja_matriculado.exists():
                raise ValidationError(f"O estudante '{aluno.nome}' já possui uma matrícula ativa nesta turma.")
        return cleaned_data
