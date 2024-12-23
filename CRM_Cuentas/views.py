from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Plan, PerfilCuenta, Cliente, TipoDispositivo, Servicio, Perfil, Cuenta, Grupo
from .forms import PerfilForm
from datetime import date, timedelta
from django.db.models import Count
from django.db import transaction
from django.db.models import Sum 
from django.http import JsonResponse
import json

def vender_plan(request, plan_id=None):
    if request.method == 'GET':
        # Obtén el plan seleccionado
        plan = Plan.objects.get(id_plan=plan_id)
        servicio_id = plan.id_servicio.id_servicio  # Obtén el servicio asociado al plan

        # Filtrar perfiles no asignados por el servicio del plan
        perfiles = list(PerfilCuenta.objects.filter(
            asignado=False,
            id_cuenta__id_servicio__id_servicio=servicio_id  # Filtrar por el servicio del plan
        ).values(
            'id_perfil_cuenta',
            'usuario',
            'pin',  # Asegúrate de incluir el PIN en los datos enviados
            'id_cuenta__correo_cuenta'
        ))

        # Obtener otros datos necesarios
        clientes = list(Cliente.objects.values('id_cliente', 'nombres'))
        dispositivos = list(TipoDispositivo.objects.values('id_tipo_dispositivo', 'descripcion'))

        return JsonResponse({
            'clientes': clientes,
            'dispositivos': dispositivos,
            'perfiles': perfiles,  # Perfiles filtrados
            'plan': {
                'id_plan': plan.id_plan,
                'numero_dispositivos': plan.numero_dispositivos,
            },
        })

    elif request.method == 'POST':
        # Obtener valores del formulario
        cliente_id = request.POST.get('id_cliente')
        dispositivo_id = request.POST.get('id_tipo_dispositivo')
        notas = request.POST.get('notas', '')  # Campo opcional
        plan_id = request.POST.get('plan_id')  # Recibe explícitamente el plan_id

        # Validar que los campos obligatorios están presentes
        if not all([cliente_id, dispositivo_id, plan_id]):
            return JsonResponse({'success': False, 'error': 'Faltan datos obligatorios.'}, status=400)

        # Obtener los perfiles seleccionados dinámicamente
        numero_dispositivos = int(Plan.objects.get(id_plan=plan_id).numero_dispositivos)
        perfiles_seleccionados = [
            request.POST.get(f'id_perfil_cuenta_{i}') for i in range(numero_dispositivos)
        ]

        # Validar que no haya perfiles repetidos
        if len(set(perfiles_seleccionados)) != len(perfiles_seleccionados):
            return JsonResponse({'success': False, 'error': 'No puedes seleccionar perfiles duplicados.'}, status=400)

        try:
            # Obtener instancias relacionadas
            cliente = Cliente.objects.get(id_cliente=cliente_id)
            dispositivo = TipoDispositivo.objects.get(id_tipo_dispositivo=dispositivo_id)
            plan = Plan.objects.get(id_plan=plan_id)

            # Crear perfiles y marcar los `PerfilCuenta` como asignados
            for i, perfil_id in enumerate(perfiles_seleccionados):
                perfil_cuenta = PerfilCuenta.objects.get(id_perfil_cuenta=perfil_id)

                # Verificar si se editaron los valores de usuario o pin
                usuario_editado = request.POST.get(f'usuario_{perfil_id}')  # Captura los datos enviados
                pin_editado = request.POST.get(f'pin_{perfil_id}')  # Captura los datos enviados

                if usuario_editado:
                    perfil_cuenta.usuario = usuario_editado  # Actualiza el usuario si se proporcionó un valor
                if pin_editado:
                    perfil_cuenta.pin = int(pin_editado)  # Actualiza el PIN si se proporcionó un valor

                perfil_cuenta.asignado = True  # Marcar como asignado
                perfil_cuenta.save()  # Guardar los cambios en la base de datos

                # Crear el perfil
                Perfil.objects.create(
                    fech_inicio=date.today(),
                    mes=plan.numero_meses,
                    notas=notas,
                    id_cliente=cliente,
                    id_perfil_cuenta=perfil_cuenta,
                    id_tipo_dispositivo=dispositivo,
                    id_plan=plan,
                )

            return JsonResponse({'success': True, 'message': 'Perfiles guardados exitosamente.'})
        except Exception as e:
            print("Error al guardar los perfiles:", str(e))
            return JsonResponse({'success': False, 'error': f'Error al guardar: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)









def agregar_cliente(request):
    if request.method == 'POST':
        # Obtener datos del POST
        nombres = request.POST.get('nombres')
        telefono = request.POST.get('telefono')

        # Validación básica
        if not nombres or not telefono:
            return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios.'}, status=400)

        # Crear el cliente
        cliente = Cliente.objects.create(nombres=nombres, telefono=telefono)
        
        # Devolver el cliente creado como respuesta JSON
        return JsonResponse({
            'success': True,
            'cliente': {
                'id_cliente': cliente.id_cliente,
                'nombres': cliente.nombres,
            },
        })

    # Si no es un POST, devolver un error
    return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)


def listar_planes(request):
    # Obtén todos los tipos de servicio
    servicios = Servicio.objects.all()

    # Obtén el ID del servicio seleccionado desde los parámetros de la URL
    servicio_id = request.GET.get('servicio_id')

    # Filtra los planes por el tipo de servicio si se selecciona uno
    if servicio_id:
        planes = Plan.objects.filter(id_servicio=servicio_id)
    else:
        planes = Plan.objects.all()

    # Contar perfiles sin asignar agrupados por servicio
    perfiles_disponibles = PerfilCuenta.objects.filter(asignado=False).values(
        'id_cuenta__id_servicio', 'id_cuenta__id_servicio__descripcion'
    ).annotate(total=Count('id_perfil_cuenta'))

    return render(request, 'planes.html', {
        'planes': planes,
        'servicios': servicios,
        'servicio_id': int(servicio_id) if servicio_id else None,
        'perfiles_disponibles': perfiles_disponibles,
    })





def admin_perfiles(request):
    from datetime import date, timedelta  # Importar para calcular fechas

    # ⚙️ Obtener la fecha de hoy y mañana
    hoy = date.today()
    manana = hoy + timedelta(days=1)
    
    # ⚙️ Capturar el filtro de vencimiento y ordenación de la URL
    filtro_vencimiento = request.GET.get('filtro_vencimiento', 'todos')  # Por defecto muestra "todos"
    sort = request.GET.get('sort', 'id_perfil')  # Campo de ordenación (por defecto id_perfil)
    order = request.GET.get('order', 'asc')  # Orden ascendente o descendente (por defecto ascendente)
    servicio_id = request.GET.get('servicio_id', None)  # ⚙️ Capturar el filtro de servicio

    # ⚙️ Obtener todos los perfiles y aplicar select_related para optimización
    order_by_field = sort if order == 'asc' else f'-{sort}'  # Definir si se ordena ascendente o descendente
    perfiles = Perfil.objects.select_related(
        'id_cliente', 
        'id_perfil_cuenta', 
        'id_perfil_cuenta__id_cuenta',
        'id_perfil_cuenta__id_cuenta__id_servicio'
    ).order_by(order_by_field)
    
    # 🔥 Aplicar filtro por estado de vencimiento
    if filtro_vencimiento == 'vencidos':
        perfiles = perfiles.filter(fech_fin__lt=hoy)
    elif filtro_vencimiento == 'hoy':
        perfiles = perfiles.filter(fech_fin=hoy)
    elif filtro_vencimiento == 'manana':
        perfiles = perfiles.filter(fech_fin=manana)

    # 🔥 Aplicar filtro por servicio (aquí está el error corregido)
    if servicio_id:
        perfiles = perfiles.filter(id_perfil_cuenta__id_cuenta__id_servicio__id_servicio=servicio_id)
        perfiles_cuenta_disponibles = PerfilCuenta.objects.filter(
            id_cuenta__id_servicio__id_servicio=servicio_id,
            asignado=False
        )
    else:
        perfiles_cuenta_disponibles = PerfilCuenta.objects.filter(asignado=False)

    # 💡 Añadir etiquetas de estado y calcular días restantes
    for perfil in perfiles:
        perfil.estado_texto = 'Activo' if perfil.estado else 'Inactivo'
        perfil.estado_clase = 'bg-green-100 text-green-700' if perfil.estado else 'bg-red-100 text-red-700'
        
        # Calcular el estado de vencimiento
        dias_restantes = (perfil.fech_fin - hoy).days if perfil.fech_fin else None
        if dias_restantes is not None:
            if dias_restantes < 0:
                perfil.estado_vencimiento = f"Vencido por {abs(dias_restantes)} días"
            elif dias_restantes == 0:
                perfil.estado_vencimiento = "Vence hoy"
            elif dias_restantes == 1:
                perfil.estado_vencimiento = "Vence mañana"
            else:
                perfil.estado_vencimiento = f"Quedan {dias_restantes} días"
        else:
            perfil.estado_vencimiento = "Fecha no asignada"

    # 🔥 Contar la cantidad de perfiles
    cantidad_perfiles = perfiles.count()  # Calcula la cantidad de perfiles

    # Contexto para la plantilla
    context = {
        "perfiles": perfiles,
        "cantidad_perfiles": cantidad_perfiles,  # Cantidad de perfiles
        "perfiles_cuenta_disponibles": perfiles_cuenta_disponibles,  # Perfiles cuenta no asignados
        "servicios": Servicio.objects.all(),  # Lista de servicios
        "servicio_id": int(servicio_id) if servicio_id else None,  # ID del servicio seleccionado
        "filtro_vencimiento": filtro_vencimiento,  # Para resaltar el filtro activo
        "sort": sort,  # Campo de ordenación
        "order": order,  # Orden ascendente o descendente
    }

    return render(request, "admin_perfiles.html", context)




def editar_perfil(request, perfil_id):
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        pin = request.POST.get("pin")

        perfil = get_object_or_404(Perfil, id_perfil=perfil_id)

        # Actualizar los valores del perfil
        perfil.id_perfil_cuenta.usuario = usuario
        perfil.id_perfil_cuenta.pin = pin
        perfil.id_perfil_cuenta.save()

        return redirect('admin_perfiles')

    return JsonResponse({"error": "Método no permitido."}, status=405)


def eliminar_perfil(request, perfil_id):
    if request.method == "POST":
        # Obtener nuevos valores del formulario
        nuevo_usuario = request.POST.get("nuevoUsuario")
        nuevo_pin = request.POST.get("nuevoPin")

        # Obtener el perfil
        perfil = get_object_or_404(Perfil, id_perfil=perfil_id)

        # Actualizar valores en PerfilCuenta asociado
        perfil.id_perfil_cuenta.usuario = nuevo_usuario
        perfil.id_perfil_cuenta.pin = nuevo_pin
        perfil.id_perfil_cuenta.asignado = False  # Cambiar el estado a False
        perfil.id_perfil_cuenta.save()

        # Eliminar el perfil
        perfil.delete()

        # Redirigir o mostrar un mensaje de éxito
        return redirect('admin_perfiles')

    return JsonResponse({"error": "Método no permitido."}, status=405)


def cambiar_perfil(request, perfil_id):
    if request.method == "POST":
        with transaction.atomic():  # 🔥 Se asegura la transacción
            # 🗃️ 1️⃣ Extraer los datos del formulario
            nuevo_perfil_cuenta_id = request.POST.get("nuevoPerfilCuenta")
            nuevo_usuario_antiguo = request.POST.get("nuevoUsuarioAntiguo")
            nuevo_pin_antiguo = request.POST.get("nuevoPinAntiguo")

            # 📚 2️⃣ Obtener los objetos necesarios
            perfil = get_object_or_404(Perfil, id_perfil=perfil_id)
            cuenta_anterior = perfil.id_perfil_cuenta
            nuevo_perfil_cuenta = get_object_or_404(PerfilCuenta, id_perfil_cuenta=nuevo_perfil_cuenta_id)

            # 🔥 3️⃣ Actualizar la cuenta anterior
            cuenta_anterior.usuario = nuevo_usuario_antiguo  # Usuario ingresado en el formulario
            cuenta_anterior.pin = nuevo_pin_antiguo  # PIN ingresado en el formulario
            cuenta_anterior.asignado = False  # Se marca como no asignado
            cuenta_anterior.save(update_fields=['usuario', 'pin', 'asignado'])

            # 🔥 4️⃣ Actualizar la nueva cuenta
            nuevo_perfil_cuenta.asignado = True  # Se marca como asignado
            nuevo_perfil_cuenta.save(update_fields=['asignado'])

            # 🔥 5️⃣ Actualizar la relación de la nueva cuenta en el perfil
            perfil.id_perfil_cuenta = nuevo_perfil_cuenta  # Se asigna la nueva cuenta
            perfil.save(update_fields=['id_perfil_cuenta'])  # Se guardan los cambios

        # 🔀 6️⃣ Redirigir a la página de administración de perfiles
        return redirect('admin_perfiles')

    return JsonResponse({"error": "Método no permitido."}, status=405)

def agregar_dia(request, perfil_id):
    if request.method == 'POST':
        try:
            perfil = get_object_or_404(Perfil, id_perfil=perfil_id)
            if perfil.fech_fin:
                perfil.fech_fin += timedelta(days=1)
                perfil.save(manual_update=True)  # Aquí se pasa manual_update=True
                return JsonResponse({'success': True, 'message': 'Día agregado correctamente.', 'nueva_fecha': perfil.fech_fin.strftime('%d-%m-%Y')})
            else:
                return JsonResponse({'success': False, 'message': 'No se pudo agregar el día. La fecha de caducidad no está establecida.'})
        except Exception as e:
            print(f"Error en agregar_dia: {str(e)}")
            return JsonResponse({'success': False, 'message': f'Ocurrió un error al intentar agregar el día: {str(e)}'})
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})


def admin_cuentas(request):
    # ⚙️ Obtener la fecha de hoy y mañana
    hoy = date.today()
    manana = hoy + timedelta(days=1)
    
    # ⚙️ Capturar el filtro de vencimiento y ordenación de la URL
    filtro_vencimiento = request.GET.get('filtro_vencimiento', 'todos')  # Por defecto muestra "todos"
    sort = request.GET.get('sort', 'id_cuenta')  # Campo de ordenación (por defecto id_cuenta)
    order = request.GET.get('order', 'asc')  # Orden ascendente o descendente (por defecto ascendente)
    servicio_id = request.GET.get('servicio_id', None)  # ⚙️ Capturar el filtro de servicio

    # ⚙️ Obtener todas las cuentas y aplicar select_related para optimización
    order_by_field = sort if order == 'asc' else f'-{sort}'  # Definir si se ordena ascendente o descendente
    cuentas = Cuenta.objects.select_related(
        'id_servicio', 
        'id_grupo', 
        'id_tipo_dispositivo'
    ).order_by(order_by_field)
    
    # 🔥 Aplicar filtro por estado de vencimiento
    if filtro_vencimiento == 'vencidos':
        cuentas = cuentas.filter(fech_fin__lt=hoy)
    elif filtro_vencimiento == 'hoy':
        cuentas = cuentas.filter(fech_fin=hoy)
    elif filtro_vencimiento == 'manana':
        cuentas = cuentas.filter(fech_fin=manana)

    # 🔥 Aplicar filtro por servicio (si se selecciona un servicio)
    if servicio_id:
        cuentas = cuentas.filter(id_servicio__id=servicio_id)

    # 💡 Añadir etiquetas de estado y calcular días restantes
    for cuenta in cuentas:
        cuenta.estado_texto = 'Activo' if cuenta.estado else 'Inactivo'
        cuenta.estado_clase = 'bg-green-100 text-green-700' if cuenta.estado else 'bg-red-100 text-red-700'
        
        # Calcular el estado de vencimiento
        dias_restantes = (cuenta.fech_fin - hoy).days if cuenta.fech_fin else None
        if dias_restantes is not None:
            if dias_restantes < 0:
                cuenta.estado_vencimiento = f"Vencido por {abs(dias_restantes)} días"
            elif dias_restantes == 0:
                cuenta.estado_vencimiento = "Vence hoy"
            elif dias_restantes == 1:
                cuenta.estado_vencimiento = "Vence mañana"
            else:
                cuenta.estado_vencimiento = f"Quedan {dias_restantes} días"
        else:
            cuenta.estado_vencimiento = "Fecha no asignada"

    # 🔥 Contar la cantidad de cuentas
    total_cuentas = cuentas.count()  # Calcula la cantidad de cuentas
    total_balance = cuentas.aggregate(Sum('mes'))['mes__sum'] or 0

    # 📊 Datos para los gráficos
    grafico_pie_datos = {
        'labels': ['Activas', 'Inactivas'],
        'values': [
            cuentas.filter(estado=True).count(),
            cuentas.filter(estado=False).count()
        ]
    }

    grafico_linea_datos = {
        'labels': [str(cuenta.fech_inicio.strftime('%b %Y')) for cuenta in cuentas],
        'values': [cuenta.mes for cuenta in cuentas]
    }

    # 📊 Crear las métricas para mostrar en el dashboard
    cuentas_activas = cuentas.filter(estado=True).count()
    cuentas_inactivas = cuentas.filter(estado=False).count()
    cuentas_vencidas = cuentas.filter(fech_fin__lt=hoy).count()
    cuentas_vencen_hoy = cuentas.filter(fech_fin=hoy).count()
    cuentas_vencen_manana = cuentas.filter(fech_fin=manana).count()

    # 🔥 Datos para el modal de creación de cuentas
    servicios = Servicio.objects.all()
    grupos = Grupo.objects.all()
    dispositivos = TipoDispositivo.objects.all()

    # Contexto para la plantilla
    context = {
        'cuentas': cuentas,
        'total_cuentas': total_cuentas,
        'total_balance': total_balance,
        'grafico_pie_datos': grafico_pie_datos,
        'grafico_linea_datos': grafico_linea_datos,
        'cuentas_activas': cuentas_activas,
        'cuentas_inactivas': cuentas_inactivas,
        'cuentas_vencidas': cuentas_vencidas,
        'cuentas_vencen_hoy': cuentas_vencen_hoy,
        'cuentas_vencen_manana': cuentas_vencen_manana,
        'filtro_vencimiento': filtro_vencimiento,  # Para resaltar el filtro activo
        'sort': sort,  # Campo de ordenación
        'order': order,  # Orden ascendente o descendente
        'servicio_id': int(servicio_id) if servicio_id else None,  # ID del servicio seleccionado
        'servicios': servicios,  # Lista de servicios para el modal
        'grupos': grupos,  # Lista de grupos para el modal
        'dispositivos': dispositivos,  # Lista de dispositivos para el modal
    }

    return render(request, 'admin_cuentas.html', context)

def editar_cuenta(request, cuenta_id):
    if request.method == 'POST':
        cuenta = get_object_or_404(Cuenta, id_cuenta=cuenta_id)

        correo = request.POST.get('correo_cuenta')
        contrasena = request.POST.get('contrasena')

        if correo:
            cuenta.correo_cuenta = correo
        if contrasena:
            cuenta.contrasena = contrasena

        cuenta.save(update_fields=['correo_cuenta', 'contrasena'])

        return JsonResponse({'success': True, 'message': 'La cuenta ha sido actualizada correctamente.'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)




def eliminar_cuenta(request, cuenta_id):
    if request.method == 'POST':
        try:
            # Obtener la cuenta que se desea eliminar
            cuenta = get_object_or_404(Cuenta, id_cuenta=cuenta_id)

            # Verificar si hay perfiles asignados a la cuenta
            perfiles_asignados = PerfilCuenta.objects.filter(id_cuenta=cuenta, asignado=True)

            if perfiles_asignados.exists():
                # Si hay perfiles asignados, devolver un error
                return JsonResponse({
                    'success': False,
                    'message': 'No se puede eliminar la cuenta porque tiene perfiles asignados.'
                }, status=400)

            # Si no hay perfiles asignados, eliminar la cuenta
            cuenta.delete()

            return JsonResponse({
                'success': True,
                'message': 'La cuenta se ha eliminado correctamente.'
            })

        except Exception as e:
            # Manejo de errores
            return JsonResponse({
                'success': False,
                'message': f'Error al intentar eliminar la cuenta: {str(e)}'
            }, status=500)

    # Si el método no es POST, devolver un error
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
