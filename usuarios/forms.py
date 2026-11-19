from django import forms
from .models import Usuario, PerfilUsuario


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


class UsuarioCadastroForm(forms.ModelForm):
    """
    Formulário para cadastro de novos usuários pelo Administrador.
    """
    password = forms.CharField(
        label='Senha Inicial de Acesso',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Defina uma senha temporária...'
        })
    )

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'perfil', 'password', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo do usuário'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@escola.gov.br'}),
            'perfil': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UsuarioEdicaoForm(forms.ModelForm):
    """
    Formulário para edição de usuários pelo Administrador.
    Permite atualizar dados cadastrais e, opcionalmente, redefinir a senha.
    """
    nova_senha = forms.CharField(
        label='Nova Senha (deixe em branco para não alterar)',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Deixe em branco para manter a senha atual...'
        })
    )

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'perfil', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo do usuário'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@escola.gov.br'}),
            'perfil': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        nova_senha = self.cleaned_data.get('nova_senha')
        if nova_senha:
            user.set_password(nova_senha)
        if commit:
            user.save()
        return user
