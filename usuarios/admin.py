from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioCustomAdmin(UserAdmin):
    model = Usuario
    list_display = ('nome', 'email', 'perfil', 'ativo', 'is_staff', 'data_criacao')
    list_filter = ('perfil', 'ativo', 'is_staff', 'is_superuser')
    search_fields = ('nome', 'email')
    ordering = ('nome',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'perfil', 'ativo')}),
        ('Permissões', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Datas Importantes', {'fields': ('last_login', 'data_criacao', 'data_atualizacao')}),
    )

    readonly_fields = ('data_criacao', 'data_atualizacao')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'perfil', 'password', 'ativo'),
        }),
    )
