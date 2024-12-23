from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Cliente, Grupo, TipoDispositivo, Servicio, Cuenta, PerfilCuenta, Plan, Perfil, HistorialRenovacion

# Registramos modelos simples
@admin.register(Cliente, Grupo, TipoDispositivo, Servicio, Plan)
class DefaultAdmin(admin.ModelAdmin):
    pass

# Definimos recursos para importar y exportar
class PerfilResource(resources.ModelResource):
    class Meta:
        model = Perfil
        fields = ('id_perfil', 'id_cliente__nombres', 'id_plan__descripcion', 'fech_inicio', 'fech_fin', 'estado')
        export_order = ('id_perfil', 'id_cliente__nombres', 'id_plan__descripcion', 'fech_inicio', 'fech_fin', 'estado')

class CuentaResource(resources.ModelResource):
    class Meta:
        model = Cuenta
        fields = ('id_cuenta', 'correo_cuenta', 'id_servicio__descripcion', 'fech_inicio', 'fech_fin', 'estado')
        export_order = ('id_cuenta', 'correo_cuenta', 'id_servicio__descripcion', 'fech_inicio', 'fech_fin', 'estado')

class HistorialRenovacionResource(resources.ModelResource):
    class Meta:
        model = HistorialRenovacion
        fields = ('id_historial', 'id_perfil__id_cliente__nombres', 'id_plan__descripcion', 'fecha_renovacion', 'meses_agregados')
        export_order = ('id_historial', 'id_perfil__id_cliente__nombres', 'id_plan__descripcion', 'fecha_renovacion', 'meses_agregados')

# Configuramos administradores con import/export
@admin.register(Perfil)
class PerfilAdmin(ImportExportModelAdmin):
    resource_class = PerfilResource
    list_display = ("id_perfil", "id_cliente", "id_plan", "fech_inicio", "fech_fin", "estado")
    list_filter = ("estado", "id_plan")
    search_fields = ("id_cliente__nombres", "id_plan__descripcion")

@admin.register(Cuenta)
class CuentaAdmin(ImportExportModelAdmin):
    resource_class = CuentaResource
    list_display = ("id_cuenta", "correo_cuenta", "id_servicio", "fech_inicio", "fech_fin", "estado")
    list_filter = ("estado", "id_servicio")
    search_fields = ("correo_cuenta", "id_servicio__descripcion")

@admin.register(HistorialRenovacion)
class HistorialRenovacionAdmin(ImportExportModelAdmin):
    resource_class = HistorialRenovacionResource
    list_display = ('id_historial', 'id_perfil', 'id_plan', 'fecha_renovacion', 'meses_agregados')
    list_filter = ('id_plan', 'fecha_renovacion')
    search_fields = ('id_perfil__id_cliente__nombres', 'id_plan__descripcion')
