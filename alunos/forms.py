from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Aluno


class AlunoForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de Alunos no SIGOE.
    """
    data_nascimento = forms.DateField(
        label='Data de Nascimento',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Informação essencial para proteção de menores e conformidade com o ECA/LGPD.'
    )

    class Meta:
        model = Aluno
        fields = ['nome', 'matricula', 'data_nascimento', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do(a) estudante',
                'autofocus': True
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 2026-00123'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula', '').strip().upper()
        # Verificar duplicidade se novo ou se mudou
        qs = Aluno.objects.filter(matricula=matricula)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Já existe um estudante cadastrado com esta matrícula.')
        return matricula

    def clean_data_nascimento(self):
        data_nasc = self.cleaned_data.get('data_nascimento')
        if data_nasc:
            if data_nasc > date.today():
                raise ValidationError('A data de nascimento não pode ser no futuro.')
            idade = (date.today() - data_nasc).days // 365
            if idade > 100:
                raise ValidationError('Data de nascimento inválida.')
        return data_nasc
