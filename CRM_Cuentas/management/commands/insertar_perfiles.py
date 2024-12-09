import os
import django
import pandas as pd
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from CRM_Cuentas.models import Cliente, Perfil, PerfilCuenta, HistorialRenovacion, Plan, Servicio, TipoDispositivo

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digitalstream.settings')
django.setup()

# Ruta del archivo Excel
file_path = 'CRM_Cuentas/management/commands/datos digitalstream 04122024.xlsx'

# Leer el archivo Excel
data = pd.read_excel(file_path)

# Filtrar las columnas necesarias
data = data[['PerfilCuenta', 'Cliente', 'Perfil', 'Telefono', 'Pin', 'Fecha ingreso', 'Meses Perfil', 'Notas', 'Servicio']]

# Función para extraer los números de la cadena Perfil_X_Y y ordenarlos
def extract_order_key(perfil_cuenta):
    match = re.match(r'Perfil_(\d+)_(\d+)', perfil_cuenta)
    if match:
        return int(match.group(2)), int(match.group(1))  # (Grupo, Posición)
    return (float('inf'), float('inf'))  # Para evitar errores con nombres no coincidentes

# Obtener y ordenar todos los PerfilCuenta de la base de datos
perfil_cuenta_queryset = PerfilCuenta.objects.all()
perfil_cuenta_ordenados = sorted(
    perfil_cuenta_queryset, 
    key=lambda pc: extract_order_key(pc.usuario)
)

# Imprimir el orden de los PerfilCuenta para verificar
print(f"Orden de los PerfilCuenta extraídos: {[pc.usuario for pc in perfil_cuenta_ordenados]}")

# Iterar por el archivo de Excel y asignar los perfiles respetando el orden
for index, (perfil_cuenta, cliente_nombre, perfil_nombre, telefono, pin, fecha_ingreso, meses_perfil, notas, servicio) in data.iterrows():
    try:
        if index >= len(perfil_cuenta_ordenados):
            print(f"No hay suficientes PerfilCuenta disponibles para asignar el perfil en la fila {index + 1}")
            break
        
        perfil_cuenta_obj = perfil_cuenta_ordenados[index] 

        if perfil_nombre:
            perfil_cuenta_obj.usuario = str(perfil_nombre).strip()
        if not pd.isnull(pin) and str(pin).isdigit():
            perfil_cuenta_obj.pin = int(pin)
        
        perfil_cuenta_obj.estado = True 
        perfil_cuenta_obj.asignado = True 
        perfil_cuenta_obj.save() 
        print(f"Actualizado PerfilCuenta: {perfil_cuenta_obj.usuario} con usuario: {perfil_cuenta_obj.usuario}, pin: {perfil_cuenta_obj.pin}, estado: {perfil_cuenta_obj.estado}, asignado: {perfil_cuenta_obj.asignado}")

        cliente = Cliente.objects.filter(
            nombres=str(cliente_nombre).strip(),
            telefono=str(telefono).strip()
        ).first()

        if not cliente:
            cliente = Cliente.objects.create(
                nombres=str(cliente_nombre).strip(),
                telefono=str(telefono).strip()
            )

        servicio_nombre = str(servicio).strip() if not pd.isnull(servicio) else None
        if servicio_nombre:
            servicio_obj = Servicio.objects.filter(descripcion=servicio_nombre).first()
            if not servicio_obj:
                print(f"Servicio no encontrado: {servicio_nombre} en la fila {index + 1}")
                continue

            plan = Plan.objects.filter(id_servicio=servicio_obj, numero_meses=1).first()
            if not plan:
                print(f"No se encontró un plan de 1 mes para el servicio: {servicio_nombre} en la fila {index + 1}")
                continue
        else:
            print(f"Servicio vacío o nulo en la fila {index + 1}.")
            continue

        fecha_inicio = pd.to_datetime(fecha_ingreso, dayfirst=True, errors='coerce') 
        if pd.isnull(fecha_inicio):
            print(f"Fecha de ingreso inválida en la fila {index + 1}")
            continue

        try:
            meses_perfil = int(meses_perfil) if not pd.isnull(meses_perfil) else 1
        except ValueError:
            print(f"Meses Perfil inválido en la fila {index + 1}, se asignará 1 por defecto.")
            meses_perfil = 1

        perfil = Perfil.objects.filter(id_perfil_cuenta=perfil_cuenta_obj).first()

        if perfil:
            perfil.fech_inicio = fecha_inicio.date() 
            perfil.mes = meses_perfil
            perfil.fech_fin = perfil.fech_inicio + relativedelta(months=meses_perfil)
            perfil.save()
            print(f"Perfil actualizado para {perfil_cuenta_obj.usuario} - Fecha inicio: {perfil.fech_inicio.strftime('%d/%m/%Y')}, Meses: {perfil.mes}, Fecha fin: {perfil.fech_fin.strftime('%d/%m/%Y')}")
        else:
            perfil = Perfil.objects.create(
                fech_inicio=fecha_inicio.date(), 
                mes=meses_perfil,
                id_cliente=cliente,
                id_perfil_cuenta=perfil_cuenta_obj,
                id_tipo_dispositivo=TipoDispositivo.objects.get(descripcion="TV"),
                id_plan=plan,
                notas=notas if not pd.isnull(notas) else "",
                estado=True
            )

            print(f"Perfil creado para {perfil_nombre} en el orden {perfil_cuenta_obj.usuario} para el cliente {cliente.nombres}")

    except Exception as e:
        print(f"Error en la fila {index + 1}: {e}")

print("Asignación de Perfiles completada.")
