from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta
import random


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=300)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return self.nombres


class Grupo(models.Model):
    id_grupo = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=300)

    def __str__(self):
        return self.descripcion


class TipoDispositivo(models.Model):
    id_tipo_dispositivo = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=300)

    def __str__(self):
        return self.descripcion


class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=300)
    precio_mayorista = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_perfiles = models.PositiveIntegerField()

    def __str__(self):
        return self.descripcion


class Cuenta(models.Model):
    id_cuenta = models.AutoField(primary_key=True)
    correo_cuenta = models.CharField(max_length=300)
    contrasena = models.CharField(max_length=300)
    fech_inicio = models.DateField(default=date.today)
    mes = models.PositiveIntegerField()
    fech_fin = models.DateField(blank=True, null=True)
    estado = models.BooleanField(default=True)
    id_servicio = models.ForeignKey('Servicio', on_delete=models.CASCADE)
    id_grupo = models.ForeignKey('Grupo', on_delete=models.CASCADE, null=True)
    id_tipo_dispositivo = models.ForeignKey('TipoDispositivo', on_delete=models.CASCADE)

    def __str__(self):
        return self.correo_cuenta

    def save(self, *args, **kwargs):
        is_admin = kwargs.pop('is_admin', False)
        manual_update = kwargs.pop('manual_update', False)  # Se extrae la variable manual_update
        is_new = self.pk is None

        # Cuando se crea una cuenta por primera vez y el usuario es admin
        if is_new and is_admin:
            super().save(*args, **kwargs)

            meses_restantes = self.mes
            fecha_actual = self.fech_inicio

            while meses_restantes > 0:
                plan = Plan.objects.filter(numero_meses__lte=meses_restantes).order_by('-numero_meses').first()
                if not plan:
                    raise Exception("No hay planes compatibles para los meses restantes.")

                HistorialRenovacion.objects.create(
                    id_cuenta=self,
                    id_plan=plan,
                    fecha_renovacion=fecha_actual,
                    meses_agregados=plan.numero_meses,
                    correo_cuenta=self.correo_cuenta,
                    contrasena_cuenta=self.contrasena,
                )

                meses_restantes -= plan.numero_meses
                fecha_actual = fecha_actual + relativedelta(months=plan.numero_meses)
        
        # Actualización de la fecha de fin si no es una actualización manual
        if not manual_update:
            self.fech_fin = self.fech_inicio + relativedelta(months=self.mes)

        super().save(*args, **kwargs)

        # Creación automática de perfiles si aún no existen
        if not PerfilCuenta.objects.filter(id_cuenta=self).exists():
            for i in range(self.id_servicio.cantidad_perfiles):
                PerfilCuenta.objects.create(
                    usuario=f"Perfil_{i + 1}_{self.id_cuenta}",
                    pin=random.randint(1000, 9999),
                    id_cuenta=self,
                    asignado=False
                )

    def dias_restantes(self):
        """Calcula los días restantes hasta la fecha de caducidad."""
        if self.fech_fin:
            return (self.fech_fin - date.today()).days
        return 0

    def estado_vencimiento(self):
        """Devuelve el estado de vencimiento de la cuenta."""
        dias_restantes = self.dias_restantes()
        if dias_restantes < 0:
            return f"Vencido por {abs(dias_restantes)} días"
        elif dias_restantes == 0:
            return "Vence hoy"
        elif dias_restantes == 1:
            return "Vence mañana"
        else:
            return f"Quedan {dias_restantes} días"
        
        

class PerfilCuenta(models.Model):
    id_perfil_cuenta = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=300)
    pin = models.PositiveIntegerField()
    id_cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    asignado = models.BooleanField()

    def __str__(self):
        return f"{self.usuario} - {self.id_cuenta.correo_cuenta}"


class Plan(models.Model):
    id_plan = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=300)
    id_servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    numero_dispositivos = models.PositiveIntegerField()
    numero_meses = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.descripcion}"


class Perfil(models.Model):
    id_perfil = models.AutoField(primary_key=True)
    fech_inicio = models.DateField(default=date.today)
    mes = models.PositiveIntegerField()
    fech_fin = models.DateField(blank=True, null=True)
    notas = models.CharField(max_length=300, blank=True)
    estado = models.BooleanField(default=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True)
    id_perfil_cuenta = models.ForeignKey(PerfilCuenta, on_delete=models.CASCADE)
    id_tipo_dispositivo = models.ForeignKey(TipoDispositivo, on_delete=models.CASCADE)
    id_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)

    def __str__(self):
        cliente_nombre = self.id_cliente.nombres if self.id_cliente else "Sin Cliente"
        return f"Perfil {self.id_perfil} - Cliente {cliente_nombre}"

    def save(self, *args, **kwargs):
        is_admin = kwargs.pop('is_admin', False)
        manual_update = kwargs.pop('manual_update', False)  # Se extrae la variable manual_update
        is_new = self.pk is None

        if is_new and is_admin:
            super().save(*args, **kwargs)

            meses_restantes = self.mes
            fecha_actual = self.fech_inicio

            while meses_restantes > 0:
                plan = Plan.objects.filter(numero_meses__lte=meses_restantes).order_by('-numero_meses').first()
                if not plan:
                    raise Exception("No hay planes compatibles para los meses restantes.")

                HistorialRenovacion.objects.create(
                    id_perfil=self,
                    id_plan=plan,
                    fecha_renovacion=fecha_actual,
                    meses_agregados=plan.numero_meses,
                    correo_cuenta=self.id_perfil_cuenta.id_cuenta.correo_cuenta,
                    contrasena_cuenta=self.id_perfil_cuenta.id_cuenta.contrasena,
                    usuario_perfil=self.id_perfil_cuenta.usuario,
                    pin_perfil=self.id_perfil_cuenta.pin,
                )

                meses_restantes -= plan.numero_meses
                fecha_actual = fecha_actual + relativedelta(months=plan.numero_meses)
        
        if not manual_update:
            self.fech_fin = self.fech_inicio + relativedelta(months=self.mes)

        super().save(*args, **kwargs)

    def dias_restantes(self):
        """Calcula los días restantes hasta la fecha de caducidad."""
        if self.fech_fin:
            return (self.fech_fin - date.today()).days
        return 0

    def estado_vencimiento(self):
        """Devuelve el mensaje de vencimiento."""
        dias_restantes = self.dias_restantes()
        if dias_restantes < 0:
            return f"Vencido por {abs(dias_restantes)} días"
        elif dias_restantes == 0:
            return "Vence hoy"
        elif dias_restantes == 1:
            return "Vence mañana"
        else:
            return f"Quedan {dias_restantes} días"

    

class HistorialRenovacion(models.Model):
    id_historial = models.AutoField(primary_key=True)
    id_perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    id_plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    fecha_renovacion = models.DateField(default=date.today)
    meses_agregados = models.PositiveIntegerField()

    correo_cuenta = models.CharField(max_length=300)
    contrasena_cuenta = models.CharField(max_length=300)
    usuario_perfil = models.CharField(max_length=300)
    pin_perfil = models.PositiveIntegerField()

    def __str__(self):
        return (
            f"Historial de Perfil {self.id_perfil.id_perfil}: "
            f"{self.fecha_renovacion} - {self.meses_agregados} meses, "
            f"Correo: {self.correo_cuenta}, Usuario: {self.usuario_perfil}"
        )
