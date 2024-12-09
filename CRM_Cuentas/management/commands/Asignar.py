import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digitalstream.settings')
django.setup()

# Importar el modelo PerfilCuenta
from CRM_Cuentas.models import PerfilCuenta

# Contador de registros actualizados
total_actualizados = PerfilCuenta.objects.update(asignado=True)

# Confirmación del número de registros actualizados
print(f"Se ha actualizado el campo 'asignado' a True en {total_actualizados} registros de PerfilCuenta.")
