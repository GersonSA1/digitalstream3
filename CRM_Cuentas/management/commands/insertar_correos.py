from django.core.management.base import BaseCommand
import pandas as pd
from django.db import connection
from CRM_Cuentas.models import Cuenta, Grupo, TipoDispositivo, Servicio
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
    help = 'Insertar datos de cuentas desde un archivo Excel'

    def handle(self, *args, **kwargs):
        # 1. Leer el archivo Excel
        file_path = "CRM_Cuentas\\management\\commands\\datos digitalstream 04122024.xlsx"
        data = pd.read_excel(file_path)

        # Convertir columnas a tipos adecuados (fecha y meses)
        data['Fecha de creacion'] = pd.to_datetime(data['Fecha de creacion'], errors='coerce')
        data['Meses'] = pd.to_numeric(data['Meses'], errors='coerce')

        # Eliminar duplicados basados en la columna 'Correo'
        data = data.drop_duplicates(subset=['Correo'])

        # 2. Eliminar datos existentes en las tablas
        self.stdout.write("Eliminando datos existentes...")
        Cuenta.objects.all().delete()
        Grupo.objects.all().delete()
        TipoDispositivo.objects.all().delete()

        # Reiniciar IDs de las tablas (en caso de SQLite)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='CRM_Cuentas_cuenta';")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='CRM_Cuentas_grupo';")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='CRM_Cuentas_tipodispositivo';")

        # 3. Crear un tipo de dispositivo predeterminado: TV
        tipo_tv, created = TipoDispositivo.objects.get_or_create(descripcion="TV")

        # 4. Insertar grupos únicos
        self.stdout.write("Insertando grupos únicos...")
        grupos_unicos = data['Grupos'].dropna().unique()
        for grupo in grupos_unicos:
            Grupo.objects.create(descripcion=str(grupo).strip())

        # 5. Procesar e insertar cuentas
        self.stdout.write("Procesando cuentas...")
        for index, row in data.iterrows():
            grupo_valor = str(row['Grupos']).strip() if not pd.isnull(row['Grupos']) else None
            grupo_obj = None

            if grupo_valor:
                try:
                    grupo_obj = Grupo.objects.get(descripcion=grupo_valor)
                except Grupo.DoesNotExist:
                    self.stdout.write(f"Grupo no encontrado: {grupo_valor}")
                    continue

            servicio_valor = str(row['Servicio']).strip() if not pd.isnull(row['Servicio']) else None
            if servicio_valor:
                try:
                    servicio_obj = Servicio.objects.get(descripcion=servicio_valor)
                except Servicio.DoesNotExist:
                    self.stdout.write(f"Servicio no encontrado: {servicio_valor}")
                    continue
            else:
                self.stdout.write(f"Servicio vacío o nulo en la fila {index + 1}.")
                continue

            # Crear la cuenta
            try:
                fech_inicio = row['Fecha de creacion']
                meses = row['Meses']

                # Verificar que ambas columnas estén bien
                if pd.isnull(fech_inicio) or pd.isnull(meses):
                    self.stdout.write(f"Datos insuficientes en la fila {index + 1}: Fecha={fech_inicio}, Meses={meses}")
                    continue

                # Sumar meses a la fecha de creación
                fech_fin = fech_inicio + relativedelta(months=int(meses))

                Cuenta.objects.create(
                    correo_cuenta=str(row['Correo']).strip(),
                    contrasena=str(row['Contraseña']).strip(),
                    fech_inicio=fech_inicio,
                    mes=meses,
                    fech_fin=fech_fin,
                    estado=True,
                    id_servicio=servicio_obj,
                    id_grupo=grupo_obj,
                    id_tipo_dispositivo=tipo_tv
                )
            except Exception as e:
                self.stdout.write(f"Error al crear la cuenta en la fila {index + 1}: {e}")

        # Confirmación final
        self.stdout.write("Datos únicos insertados correctamente en las tablas Cuenta, Grupo y TipoDispositivo.")
