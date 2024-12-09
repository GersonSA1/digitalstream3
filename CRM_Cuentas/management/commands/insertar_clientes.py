import os
import re
import pandas as pd
from django.db import connection
from django.core.management.base import BaseCommand
from CRM_Cuentas.models import Cliente

class Command(BaseCommand):
    help = 'Inserta los clientes desde un archivo Excel'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando la inserción de clientes...')

        try:
            # 1️⃣ Eliminar todos los datos existentes en la tabla Cliente
            Cliente.objects.all().delete()
            self.stdout.write(self.style.WARNING('Todos los clientes existentes han sido eliminados.'))

            # 2️⃣ Reiniciar el ID de la tabla Cliente (resetear el contador)
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='CRM_Cuentas_cliente';")
            self.stdout.write(self.style.WARNING('ID de la tabla Cliente reiniciado.'))

            # 3️⃣ Leer el archivo Excel y filtrar datos válidos
            file_path = 'CRM_Cuentas/management/commands/datos digitalstream 04122024.xlsx'
            
            # Verificar si el archivo existe
            if not os.path.isfile(file_path):
                self.stdout.write(self.style.ERROR(f"El archivo {file_path} no existe."))
                return

            # Cargar el archivo Excel
            data = pd.read_excel(file_path)

            # Validar que las columnas 'Cliente' y 'Telefono' existan
            required_columns = ['Cliente', 'Telefono']
            if not all(col in data.columns for col in required_columns):
                self.stdout.write(self.style.ERROR(f"El archivo Excel debe contener las columnas: {required_columns}"))
                return

            # Asegurar que los datos sean cadenas y filtrar valores válidos
            clientes_validos = data[
                (data['Cliente'].notnull()) & 
                (data['Telefono'].notnull()) & 
                (data['Telefono'].astype(str).str.strip() != '')
            ]

            # Eliminar duplicados basados en las columnas 'Cliente' y 'Telefono'
            clientes_validos = clientes_validos.drop_duplicates(subset=['Cliente', 'Telefono'])

            # Función para formatear los números de teléfono
            def format_phone(phone):
                """Elimina caracteres no numéricos y aplica el formato internacional para teléfonos de Ecuador."""
                phone = re.sub(r'\D', '', str(phone))
                if phone.startswith("593") and len(phone) == 12:
                    return f"+593 {phone[3:5]} {phone[5:8]} {phone[8:]}"
                elif len(phone) == 10:  # Caso sin el prefijo de país
                    return f"+593 {phone[:2]} {phone[2:5]} {phone[5:]}"
                else:
                    return phone  # Devolver sin cambios si no cumple con el formato esperado

            # Aplicar formato a la columna 'Telefono'
            clientes_validos['Telefono'] = clientes_validos['Telefono'].apply(format_phone)

            # 4️⃣ Insertar datos únicos en la base de datos
            total_registros = 0
            for index, row in clientes_validos.iterrows():
                # Normalizar nombre del cliente
                cliente_nombres = ''.join(e for e in str(row['Cliente']).lower().strip() if e.isalnum())
                cliente_telefono = ''.join(e for e in str(row['Telefono']) if e.isdigit())

                cliente, created = Cliente.objects.get_or_create(
                    nombres=cliente_nombres,
                    telefono=cliente_telefono,
                    defaults={
                        'nombres': row['Cliente'],
                        'telefono': row['Telefono']
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Cliente creado: {cliente.nombres}"))
                    total_registros += 1
                else:
                    self.stdout.write(self.style.WARNING(f"Cliente ya existente: {cliente.nombres}"))

            self.stdout.write(self.style.SUCCESS(f"Datos únicos, formateados, IDs reiniciados, y {total_registros} registros insertados correctamente."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
