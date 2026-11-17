from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import LoginForm
from .models import Usuario


def login_view(request):
    """
    View responsável pela autenticação de usuários no SIGOE.
    Redireciona usuários já autenticados para a página inicial.
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    redirect_to = request.POST.get('next', request.GET.get('next', ''))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            lembrar_me = form.cleaned_data.get('lembrar_me', False)

            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.ativo and user.is_active:
                    auth_login(request, user)

                    # Configuração do tempo de sessão
                    if not lembrar_me:
                        # Expira ao fechar o navegador
                        request.session.set_expiry(0)
                    else:
                        # 2 semanas de persistência (padrão Django)
                        request.session.set_expiry(1209600)

                    messages.success(request, f"Olá, {user.nome}! Seja bem-vindo(a) ao SIGOE.")

                    # Validação de segurança para redirecionamento
                    if redirect_to and url_has_allowed_host_and_scheme(
                        url=redirect_to,
                        allowed_hosts={request.get_host()},
                        require_https=request.is_secure()
                    ):
                        return redirect(redirect_to)
                    return redirect('core:home')
                else:
                    messages.error(
                        request,
                        "Sua conta de acesso está inativa no sistema. Por favor, contate o administrador escolar."
                    )
            else:
                # Verifica se o email existe para mensagem mais amigável sem vazar dados sensíveis
                user_exists = Usuario.objects.filter(email=email).exists()
                if user_exists and not Usuario.objects.filter(email=email, ativo=True).exists():
                    messages.error(request, "Usuário desativado na instituição. Procure a gestão escolar.")
                else:
                    messages.error(request, "E-mail ou senha incorretos. Verifique suas credenciais e tente novamente.")
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {
        'form': form,
        'next': redirect_to
    })


def logout_view(request):
    """
    Encerra a sessão atual com segurança e redireciona para a tela de login.
    """
    if request.user.is_authenticated:
        auth_logout(request)
        messages.info(request, "Você encerrou sua sessão no SIGOE com segurança.")
    return redirect('usuarios:login')
