from django.contrib import admin
from .models import Cliente, Grupo, TipoDispositivo, Servicio, Cuenta, PerfilCuenta, Plan, Perfil
from CRM_Cuentas.models import Perfil, HistorialRenovacion

admin.site.register(Cliente)
admin.site.register(Grupo)
admin.site.register(TipoDispositivo)
admin.site.register(Servicio)
admin.site.register(Cuenta)
admin.site.register(PerfilCuenta)
admin.site.register(Plan)


class HistorialRenovacionInline(admin.TabularInline):
    model = HistorialRenovacion
    extra = 0
    fields = ('fecha_renovacion', 'meses_agregados', 'correo_cuenta', 'usuario_perfil', 'id_plan')


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("id_perfil", "id_cliente", "fech_inicio", "fech_fin", "estado")
    inlines = [HistorialRenovacionInline]

    def save_model(self, request, obj, form, change):
        # Pasa el flag `is_admin` al método save del modelo
        obj.save(is_admin=True)


@admin.register(HistorialRenovacion)
class HistorialRenovacionAdmin(admin.ModelAdmin):
    list_display = ('id_perfil', 'fecha_renovacion', 'meses_agregados', 'correo_cuenta', 'usuario_perfil', 'id_plan')
    search_fields = ('correo_cuenta', 'usuario_perfil', 'id_plan__descripcion')
    list_filter = ('id_plan', 'fecha_renovacion')
