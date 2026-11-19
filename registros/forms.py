from django import forms
from django.utils import timezone
from .models import Ocorrencia, CategoriaOcorrencia
from turmas.models import MatriculaTurma, SituacaoMatricula


class OcorrenciaForm(forms.ModelForm):
    """
    Formulário para registro de ocorrências pelos professores e gestores.
    Conforme o princípio pedagógico, incentiva relato descritivo e objetivo.
    """
    matricula_turma = forms.ModelChoiceField(
        queryset=MatriculaTurma.objects.filter(
            situacao=SituacaoMatricula.ATIVA,
            aluno__ativo=True,
            turma__ativa=True
        ).select_related('aluno', 'turma').order_by('turma__nome', 'aluno__nome'),
        label='Estudante e Turma',
        empty_label='Selecione o estudante...',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_matricula_turma'})
    )
    categoria = forms.ModelChoiceField(
        queryset=CategoriaOcorrencia.objects.filter(ativo=True).order_by('nome'),
        label='Categoria da Ocorrência',
        empty_label='Selecione a categoria...',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_categoria'})
    )
    data_ocorrencia = forms.DateTimeField(
        label='Data e Horário do Fato',
        initial=timezone.now,
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
    )
    local = forms.CharField(
        label='Local do Fato',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Sala de Aula 3, Pátio Central, Refeitório, Quadra',
            'id': 'id_local'
        })
    )
    descricao = forms.CharField(
        label='Descrição Objetiva e Fática',
        help_text='Atenção: Descreva os fatos de maneira estritamente descritiva e objetiva, evitando rótulos ou juízos de valor.',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Relate o ocorrido de forma fática e imparcial...',
            'id': 'id_descricao'
        })
    )
    providencias_iniciais = forms.CharField(
        label='Providências Iniciais Adotadas',
        required=False,
        help_text='Ações de mediação ou diálogo tomadas de imediato.',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ex: Conversa individual com o estudante, orientações sobre as normas...',
            'id': 'id_providencias_iniciais'
        })
    )

    class Meta:
        model = Ocorrencia
        fields = [
            'matricula_turma',
            'categoria',
            'data_ocorrencia',
            'local',
            'descricao',
            'providencias_iniciais'
        ]


class CategoriaOcorrenciaForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de Categorias de Ocorrência.
    """
    class Meta:
        model = CategoriaOcorrencia
        fields = ['nome', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Indisciplina, Conflito entre pares, Atitude Colaborativa',
                'autofocus': True
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição e orientações de enquadramento pedagógico desta categoria...'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
