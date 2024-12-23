from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_planes, name='planes'),  # Página principal de planes
    path('planes/vender/<int:plan_id>/', views.vender_plan, name='vender_plan'),
    path('clientes/agregar/', views.agregar_cliente, name='agregar_cliente'),

    path('perfiles/', views.admin_perfiles, name='admin_perfiles'),
    path('perfiles/editar/<int:perfil_id>/', views.editar_perfil, name='editar_perfil'),
    path('eliminar_perfil/<int:perfil_id>/', views.eliminar_perfil, name='eliminar_perfil'),

    path('cambiar_perfil/<int:perfil_id>/', views.cambiar_perfil, name='cambiar_perfil'),

    path('agregar_dia/<int:perfil_id>/', views.agregar_dia, name='agregar_dia'),

    path('cuentas/', views.admin_cuentas, name='admin_cuentas'),
    path('editar_cuenta/<int:cuenta_id>/', views.editar_cuenta, name='editar_cuenta'),
    path('eliminar_cuenta/<int:cuenta_id>/', views.eliminar_cuenta, name='editar_cuenta'),


]
