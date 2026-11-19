from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UsuarioManager(BaseUserManager):
    """Gerenciador customizado para o modelo de Usuário utilizando o email como identificador único."""

    def create_user(self, email, nome, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        if not nome:
            raise ValueError('O nome completo é obrigatório.')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('ativo', True)

        username = extra_fields.pop('username', None) or email

        user = self.model(email=email, nome=nome, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('ativo', True)
        extra_fields.setdefault('perfil', PerfilUsuario.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')

        return self.create_user(email, nome, password, **extra_fields)


class PerfilUsuario(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrador'
    PROFESSOR = 'PROFESSOR', 'Professor'
    COORDENACAO = 'COORDENACAO', 'Coordenação Pedagógica'


class Usuario(AbstractUser):
    """
    Modelo de Usuário personalizado para o SIGOE.
    Atende aos perfis: Administrador, Professor e Coordenação Pedagógica.
    """
    username = models.CharField(
        'Nome de Usuário',
        max_length=150,
        unique=True,
        blank=True,
        null=True
    )
    nome = models.CharField(
        'Nome Completo',
        max_length=150
    )
    email = models.EmailField(
        'E-mail',
        unique=True
    )
    perfil = models.CharField(
        'Perfil',
        max_length=20,
        choices=PerfilUsuario.choices,
        default=PerfilUsuario.PROFESSOR
    )
    ativo = models.BooleanField(
        'Ativo',
        default=True,
        help_text='Indica se este usuário possui acesso ativo ao sistema.'
    )
    data_criacao = models.DateTimeField(
        'Data de Criação',
        auto_now_add=True
    )
    data_atualizacao = models.DateTimeField(
        'Data de Atualização',
        auto_now=True
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['perfil', 'ativo'], name='usuario_perfil_ativo_idx'),
        ]

    def __str__(self):
        return f"{self.nome} ({self.get_perfil_display()})"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        self.is_active = self.ativo
        if self.perfil == PerfilUsuario.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        return self.perfil == PerfilUsuario.ADMIN or self.is_superuser

    @property
    def is_professor(self):
        return self.perfil == PerfilUsuario.PROFESSOR

    @property
    def is_coordenacao(self):
        return self.perfil == PerfilUsuario.COORDENACAO
