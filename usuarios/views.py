from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import LoginForm, UsuarioCadastroForm
from .models import Usuario, PerfilUsuario
from .decorators import admin_required
from registros.models import Ocorrencia, CategoriaOcorrencia
from turmas.models import Turma
from alunos.models import Aluno


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
                        request.session.set_expiry(0)
                    else:
                        request.session.set_expiry(1209600)

                    messages.success(request, f"Olá, {user.nome}! Seja bem-vindo(a) ao SIGOE.")

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


@login_required
@admin_required
def painel_admin_view(request):
    """
    Painel de Gestão Administrativa do SIGOE.
    Permite gerenciar usuários, cadastros base e acompanhar auditoria.
    """
    perfil_filtro = request.GET.get('perfil')
    busca = request.GET.get('busca', '').strip()

    usuarios = Usuario.objects.all().order_by('nome')
    if perfil_filtro:
        usuarios = usuarios.filter(perfil=perfil_filtro)
    if busca:
        usuarios = usuarios.filter(nome__icontains=busca) | usuarios.filter(email__icontains=busca)

    # Novo cadastro via modal ou form
    if request.method == 'POST':
        cadastro_form = UsuarioCadastroForm(request.POST)
        if cadastro_form.is_valid():
            novo_usuario = cadastro_form.save()
            messages.success(
                request,
                f"Usuário '{novo_usuario.nome}' ({novo_usuario.email}) cadastrado com sucesso!"
            )
            return redirect('usuarios:painel_admin')
        else:
            messages.error(request, "Verifique os erros no formulário de cadastro de usuário.")
    else:
        cadastro_form = UsuarioCadastroForm()

    context = {
        'usuarios': usuarios,
        'cadastro_form': cadastro_form,
        'perfil_choices': PerfilUsuario.choices,
        'perfil_selecionado': perfil_filtro,
        'busca': busca,
        # Estatísticas consolidadas
        'total_usuarios': Usuario.objects.count(),
        'total_professores': Usuario.objects.filter(perfil=PerfilUsuario.PROFESSOR).count(),
        'total_coordenacao': Usuario.objects.filter(perfil=PerfilUsuario.COORDENACAO).count(),
        'total_admins': Usuario.objects.filter(perfil=PerfilUsuario.ADMIN).count(),
        'total_turmas': Turma.objects.count(),
        'total_alunos': Aluno.objects.count(),
        'total_categorias': CategoriaOcorrencia.objects.count(),
        'total_ocorrencias': Ocorrencia.objects.count(),
    }
    return render(request, 'usuarios/painel_admin.html', context)


@login_required
@admin_required
def toggle_status_usuario_view(request, pk):
    """
    Ativa ou desativa o acesso de um determinado usuário.
    Impede que o administrador desative a si próprio.
    """
    usuario_alvo = get_object_or_404(Usuario, pk=pk)

    if usuario_alvo == request.user:
        messages.warning(request, "Por motivos de segurança, você não pode desativar seu próprio usuário.")
        return redirect('usuarios:painel_admin')

    usuario_alvo.ativo = not usuario_alvo.ativo
    usuario_alvo.is_active = usuario_alvo.ativo
    usuario_alvo.save()

    status_str = "ativado" if usuario_alvo.ativo else "desativado"
    messages.success(request, f"Usuário '{usuario_alvo.nome}' foi {status_str} com sucesso.")
    return redirect('usuarios:painel_admin')
