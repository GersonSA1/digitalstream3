import os
import django
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from CRM_Cuentas.models import Perfil

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digitalstream.settings')
django.setup()

# **Lista completa de fechas de inicio en formato dd/mm/yyyy**
fechas_inicio = [
    '17/5/2024', '21/10/2024', '20/11/2024', '24/11/2024', '21/11/2024', '21/11/2024', '11/11/2024', '3/11/2024', 
    '28/5/2024', '19/11/2024', '29/11/2024', '28/10/2024', '18/10/2024', '29/11/2022', '24/10/2024', '4/12/2024', 
    '4/12/2024', '29/11/2024', '19/11/2024', '21/11/2024', '21/11/2024', '1/12/2024', '30/10/2024', '24/10/2024',
    '24/10/2024', '6/4/2023', '6/4/2023', '6/4/2023', '6/4/2023', '6/4/2023', '5/5/2024', '1/10/2023', 
    '14/10/2024', '30/11/2024', '28/11/2024', '2/12/2024', '30/9/2024', '5/11/2024', '16/11/2024', '13/9/2024',
    '24/11/2024', '20/9/2024', '8/9/2024', '6/12/2024', '13/9/2024', '13/11/2024', '10/10/2024', '28/10/2024',
    '6/12/2024', '6/12/2024', '6/12/2024', '2/11/2022', '20/9/2024', '13/9/2024', '2/12/2024', '9/11/2024', 
    '11/8/2022', '30/11/2024', '5/8/2024', '27/3/2023', '10/10/2024', '13/11/2024', '12/10/2024', '16/6/2023',
    '27/11/2024', '24/11/2024', '8/5/2024', '23/11/2024', '5/8/2024', '17/11/2024', '29/11/2024', '3/12/2024',
    '15/8/2023', '21/9/2024', '8/9/2024', '15/1/2024', '18/11/2024', '16/5/2024', '31/8/2024', '28/11/2024'
]

# **Lista completa de meses para cada perfil**
meses = [
    7, 2, 1, 1, 1, 1, 1, 3, 9, 1, 1, 2, 2, 26, 2, 1, 1, 1, 2, 1, 1, 1, 3, 2, 
    2, 4, 4, 4, 4, 4, 8, 15, 2, 1, 1, 2, 3, 1, 1, 3, 1, 3, 3, 1, 3, 1, 2, 2, 
    1, 1, 1, 26, 3, 1, 3, 1, 1, 28, 1, 4, 20, 2, 1, 2, 19, 1, 1, 7, 1, 4, 1, 
    1, 1, 16, 3, 3, 13, 1, 7, 4, 1, 15, 4, 1, 1, 9, 9, 9, 9, 9, 6, 1, 4, 1, 
    2, 2, 4, 25, 4, 4, 4, 4, 4, 4, 21, 21, 21, 21, 21, 12, 2, 3, 2, 3, 9, 9, 
    9, 13, 50, 25, 2, 2, 3, 3, 9, 1, 3, 2, 3, 1, 2, 1, 1, 1, 3, 1, 2, 1, 1, 
    3, 5, 1, 1, 3, 1, 1, 1, 2, 3, 4, 1, 3, 2, 6, 2, 2, 5, 29, 1, 1, 1, 1, 1
]

# **Función para convertir la fecha en formato dd/mm/yyyy o mm/dd/yyyy a un objeto de fecha**
def parse_fecha(fecha):
    try:
        fecha_dt = datetime.strptime(fecha, '%d/%m/%Y').date()
    except ValueError:
        try:
            fecha_dt = datetime.strptime(fecha, '%m/%d/%Y').date()
        except ValueError:
            fecha_dt = None
    return fecha_dt

# **Convertir todas las fechas a objetos de fecha**
fechas_inicio = [parse_fecha(fecha) for fecha in fechas_inicio]

# Obtener y ordenar todos los perfiles de la base de datos
perfil_queryset = Perfil.objects.all()
perfil_ordenados = perfil_queryset.order_by('id_perfil')

# **Actualizar las fechas de inicio y meses en los perfiles**
for index, perfil in enumerate(perfil_ordenados):
    try:
        if index >= len(fechas_inicio) or index >= len(meses):
            print(f"No hay suficientes fechas de inicio o meses para la fila {index + 1}")
            break

        nueva_fecha_inicio = fechas_inicio[index]
        nuevos_meses = meses[index]

        if nueva_fecha_inicio is None:
            print(f"Fecha inválida en la fila {index + 1}. Se omite esta actualización.")
            continue

        perfil.fech_inicio = nueva_fecha_inicio
        perfil.mes = nuevos_meses
        perfil.fech_fin = perfil.fech_inicio + relativedelta(months=perfil.mes)

        perfil.save()
        print(f"Perfil actualizado - ID: {perfil.id_perfil}, Fecha de inicio: {perfil.fech_inicio}, Meses: {perfil.mes}, Fecha de fin: {perfil.fech_fin}")
    except Exception as e:
        print(f"Error en la fila {index + 1}: {e}")

# Confirmación
print("Actualización de fechas de inicio y meses completada.")
