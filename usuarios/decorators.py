from functools import wraps
from django.shortcuts import redirect, render
from django.contrib import messages
from usuarios.models import PerfilUsuario


def perfil_required(perfis_permitidos):
    """
    Decorator que restringe o acesso a uma view aos perfis de usuário especificados.
    O Administrador (ou superusuário) tem acesso automático por padrão.
    """
    if isinstance(perfis_permitidos, str):
        perfis_permitidos = [perfis_permitidos]

    # Sempre permite que administradores acessem
    perfis_completos = set(perfis_permitidos)
    perfis_completos.add(PerfilUsuario.ADMIN)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"/usuarios/login/?next={request.path}")

            if request.user.is_superuser or request.user.perfil in perfis_completos:
                return view_func(request, *args, **kwargs)

            # Usuário autenticado mas sem perfil autorizado
            messages.warning(
                request,
                f"Acesso restrito. Seu perfil ({request.user.get_perfil_display()}) não possui permissão para acessar esta área."
            )
            return render(request, '403.html', {
                'perfis_permitidos': [
                    dict(PerfilUsuario.choices).get(p, p) for p in perfis_permitidos
                ]
            }, status=403)

        return _wrapped_view
    return decorator


def professor_required(view_func):
    """Permite acesso apenas a Professores e Administradores."""
    return perfil_required([PerfilUsuario.PROFESSOR])(view_func)


def coordenacao_required(view_func):
    """Permite acesso apenas à Coordenação Pedagógica e Administradores."""
    return perfil_required([PerfilUsuario.COORDENACAO])(view_func)


def admin_required(view_func):
    """Permite acesso exclusivo a Administradores."""
    return perfil_required([PerfilUsuario.ADMIN])(view_func)


def professor_ou_coordenacao_required(view_func):
    """Permite acesso a Professores, Coordenação e Administradores."""
    return perfil_required([PerfilUsuario.PROFESSOR, PerfilUsuario.COORDENACAO])(view_func)
