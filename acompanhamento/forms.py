from django import forms
from .models import Acompanhamento, TipoRegistroAcompanhamento
from registros.models import StatusOcorrencia


class AcompanhamentoForm(forms.ModelForm):
    """
    Formulário para a Coordenação Pedagógica registrar intervenções,
    reuniões com responsáveis, orientações e encaminhamentos externos.
    """
    tipo_registro = forms.ChoiceField(
        choices=TipoRegistroAcompanhamento.choices,
        label='Tipo de Intervenção Pedagógica',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_registro'})
    )
    observacao = forms.CharField(
        label='Parecer Pedagógico / Observações da Reunião',
        help_text='Relato detalhado da conversa, postura do estudante ou diálogo com os pais.',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Descreva detalhadamente a ação pedagógica ou ata de reunião realizada...'
        })
    )
    encaminhamento = forms.CharField(
        label='Encaminhamentos e Deliberações',
        required=False,
        help_text='Ações combinadas, termos assinados ou encaminhamentos a órgãos externos.',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ex: Encaminhado para apoio psicopedagógico; retorno agendado em 15 dias...'
        })
    )

    class Meta:
        model = Acompanhamento
        fields = ['tipo_registro', 'observacao', 'encaminhamento']


class AlterarStatusForm(forms.Form):
    """
    Formulário para tramitar o status do ciclo de vida da ocorrência.
    """
    novo_status = forms.ChoiceField(
        choices=StatusOcorrencia.choices,
        label='Novo Status de Tramitação',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    justificativa = forms.CharField(
        label='Justificativa da Alteração de Status',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Breve justificativa para a trilha de auditoria...'
        })
    )
