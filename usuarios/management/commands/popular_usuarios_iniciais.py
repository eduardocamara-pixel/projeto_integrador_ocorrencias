from django.core.management.base import BaseCommand
from usuarios.models import Usuario, PerfilUsuario


USUARIOS_INICIAIS = [
    {
        'email': 'admin@escola.gov.br',
        'nome': 'Administrador Geral',
        'password': 'admin@sigoe2026',
        'perfil': PerfilUsuario.ADMIN,
        'is_superuser': True,
        'is_staff': True,
    },
    {
        'email': 'coordenacao@escola.gov.br',
        'nome': 'Coordenação Pedagógica',
        'password': 'coord@sigoe2026',
        'perfil': PerfilUsuario.COORDENACAO,
        'is_superuser': False,
        'is_staff': False,
    },
    {
        'email': 'professor@escola.gov.br',
        'nome': 'Prof. Carlos Eduardo',
        'password': 'prof@sigoe2026',
        'perfil': PerfilUsuario.PROFESSOR,
        'is_superuser': False,
        'is_staff': False,
    },
]


class Command(BaseCommand):
    help = 'Cadastra usuários iniciais padrão para testes dos 3 perfis: Admin, Coordenação e Professor.'

    def handle(self, *args, **options):
        for user_data in USUARIOS_INICIAIS:
            email = user_data['email']
            user = Usuario.objects.filter(email=email).first()
            if not user:
                user = Usuario.objects.create_user(
                    email=email,
                    nome=user_data['nome'],
                    password=user_data['password'],
                    perfil=user_data['perfil'],
                    is_superuser=user_data['is_superuser'],
                    is_staff=user_data['is_staff'],
                )
                self.stdout.write(self.style.SUCCESS(
                    f"[+] Usuário criado: {user.nome} ({user.email}) - Perfil: {user.get_perfil_display()}"
                ))
            else:
                self.stdout.write(f"[-] Usuário já existente: {user.email}")

        self.stdout.write(self.style.SUCCESS('\nCarga de usuários de teste finalizada com sucesso!'))
