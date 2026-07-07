import csv
import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import IncidenteForm
from .models import Incidente, HistorialIncidente


def inicio(request):
    return render(request, 'inicio.html')


@login_required
def registrar_incidente(request):
    if request.method == 'POST':
        form = IncidenteForm(request.POST, request.FILES)
        if form.is_valid():
            incidente = form.save(commit=False)
            incidente.creado_por = request.user
            incidente.save()
            messages.success(request, 'Incidente registrado correctamente.')
            return redirect('lista_incidentes')
    else:
        form = IncidenteForm()

    return render(
        request,
        'registrar_incidente.html',
        {'form': form, 'modo': 'crear'},
    )


@login_required
def lista_incidentes(request):
    incidentes = (
        Incidente.objects
        .select_related('responsable', 'creado_por')
        .all()
        .order_by('-fecha', '-creado_en')
    )

    busqueda = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    riesgo = request.GET.get('riesgo', '').strip()

    if busqueda:
        incidentes = incidentes.filter(
            Q(descripcion__icontains=busqueda)
            | Q(ubicacion__icontains=busqueda)
            | Q(tipo__icontains=busqueda)
        )

    if estado:
        incidentes = incidentes.filter(estado=estado)

    if riesgo:
        incidentes = incidentes.filter(riesgo=riesgo)

    paginator = Paginator(incidentes, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    contexto = {
        'page_obj': page_obj,
        'incidentes': page_obj.object_list,
        'busqueda': busqueda,
        'estado_actual': estado,
        'riesgo_actual': riesgo,
        'estados': Incidente.ESTADOS,
        'riesgos': Incidente.NIVEL_RIESGO,
    }
    return render(request, 'lista_incidentes.html', contexto)


@login_required
def editar_incidente(request, id):
    incidente = get_object_or_404(Incidente, id=id)

    # Seguridad RBAC:
    # Un operador común solo puede editar incidentes que él reportó y que sigan en estado pendiente.
    es_supervisor = request.user.groups.filter(name='Supervisor').exists() or request.user.is_superuser
    if not es_supervisor and (incidente.creado_por != request.user or incidente.estado != 'pendiente'):
        messages.error(request, 'Acceso denegado: Solo puedes editar tus propios reportes en estado pendiente.')
        return redirect('lista_incidentes')

    if request.method == 'POST':
        estado_previo = incidente.estado
        responsable_previo = incidente.responsable.username if incidente.responsable else "Sin asignar"

        form = IncidenteForm(request.POST, request.FILES, instance=incidente)
        if form.is_valid():
            instancia = form.save(commit=False)
            instancia.save()

            # Registrar en la bitácora si cambió el estado
            if estado_previo != instancia.estado:
                HistorialIncidente.objects.create(
                    incidente=instancia,
                    usuario=request.user,
                    campo_modificado="Estado",
                    valor_anterior=estado_previo.capitalize(),
                    valor_nuevo=instancia.get_estado_display(),
                    detalle=f"Estado cambiado a {instancia.get_estado_display()}."
                )

            messages.success(request, 'Incidente actualizado y registrado en bitácora.')
            return redirect('lista_incidentes')
    else:
        form = IncidenteForm(instance=incidente)

    historial = incidente.historial.select_related('usuario').all()
    return render(
        request,
        'registrar_incidente.html',
        {
            'form': form,
            'modo': 'editar',
            'incidente': incidente,
            'historial': historial
        },
    )


@login_required
def eliminar_incidente(request, id):
    incidente = get_object_or_404(Incidente, id=id)

    # Seguridad RBAC:
    # Solo los supervisores o administradores pueden eliminar incidentes.
    es_supervisor = request.user.groups.filter(name='Supervisor').exists() or request.user.is_superuser
    if not es_supervisor:
        messages.error(request, 'Acceso denegado: Solo los supervisores pueden eliminar incidentes.')
        return redirect('lista_incidentes')

    if request.method == 'POST':
        incidente.delete()
        messages.success(request, 'Incidente eliminado correctamente.')
        return redirect('lista_incidentes')

    return render(request, 'confirmar_eliminar.html', {'incidente': incidente})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            messages.success(request, 'Sesión iniciada correctamente.')
            return redirect(next_url or 'dashboard')

        return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')


@login_required
def dashboard(request):
    incidentes = Incidente.objects.select_related('responsable', 'creado_por')
    total = incidentes.count()
    pendientes = incidentes.filter(estado='pendiente').count()
    en_proceso = incidentes.filter(estado='en_proceso').count()
    resueltos = incidentes.filter(estado='resuelto').count()
    criticos = incidentes.filter(riesgo='critico').count()

    # Agrupación para gráficos del Dashboard Avanzado
    # 1. Por tipo
    por_tipo = incidentes.values('tipo').annotate(total=Count('id'))
    datos_tipo = {item['tipo']: item['total'] for item in por_tipo}

    # 2. Por riesgo
    por_riesgo = incidentes.values('riesgo').annotate(total=Count('id'))
    datos_riesgo = {item['riesgo']: item['total'] for item in por_riesgo}

    # 3. Actividad reciente: últimos 8 cambios registrados en la bitácora
    actividades_recientes = (
        HistorialIncidente.objects
        .select_related('usuario', 'incidente')
        .order_by('-fecha_cambio')[:8]
    )

    contexto = {
        'total': total,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'resueltos': resueltos,
        'criticos': criticos,
        'actividades_recientes': actividades_recientes,
        'grafico_tipo_json': json.dumps(datos_tipo),
        'grafico_riesgo_json': json.dumps(datos_riesgo),
    }

    return render(request, 'dashboard.html', contexto)


@login_required
def exportar_incidentes_csv(request):
    """Exportación a Excel / CSV con filtros de consulta activos"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_incidentes_somasafe.csv"'

    # Forzar codificación UTF-8 con BOM para soporte nativo de Excel con tildes
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'ID',
        'Tipo',
        'Fecha',
        'Ubicación',
        'Estado',
        'Riesgo',
        'Responsable',
        'Reportado Por',
        'Fecha de Registro'
    ])

    incidentes = Incidente.objects.select_related('responsable', 'creado_por').all()
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    riesgo = request.GET.get('riesgo', '')

    if q:
        incidentes = incidentes.filter(
            Q(descripcion__icontains=q)
            | Q(ubicacion__icontains=q)
            | Q(tipo__icontains=q)
        )
    if estado:
        incidentes = incidentes.filter(estado=estado)
    if riesgo:
        incidentes = incidentes.filter(riesgo=riesgo)

    for inc in incidentes:
        resp = inc.responsable.username if inc.responsable else "No asignado"
        creador = inc.creado_por.username if inc.creado_por else "Sistema"
        writer.writerow([
            inc.id,
            inc.get_tipo_display(),
            inc.fecha,
            inc.ubicacion,
            inc.get_estado_display(),
            inc.get_riesgo_display(),
            resp,
            creador,
            inc.creado_en.strftime('%d/%m/%Y %H:%M')
        ])

    return response
