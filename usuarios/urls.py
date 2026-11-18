from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-painel/', views.painel_admin_view, name='painel_admin'),
    path('admin-painel/usuario/<int:pk>/toggle-status/', views.toggle_status_usuario_view, name='toggle_status_usuario'),
]
