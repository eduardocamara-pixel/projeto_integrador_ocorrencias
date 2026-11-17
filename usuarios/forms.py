from django import forms


class LoginForm(forms.Form):
    """
    Formulário de autenticação do SIGOE.
    Utiliza o e-mail como credencial principal de acesso.
    """
    email = forms.EmailField(
        label='E-mail Institucional',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemplo@escola.gov.br',
            'autocomplete': 'email',
            'autofocus': True,
            'id': 'id_email',
        })
    )
    password = forms.CharField(
        label='Senha de Acesso',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Informe sua senha',
            'autocomplete': 'current-password',
            'id': 'id_password',
        })
    )
    lembrar_me = forms.BooleanField(
        label='Lembrar-me neste dispositivo',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_lembrar_me',
        })
    )
