from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import IncidenteForm
from .models import Incidente


def inicio(request):
    return render(request, 'inicio.html')


@login_required
def registrar_incidente(request):
    if request.method == 'POST':
        form = IncidenteForm(request.POST)
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

    if request.method == 'POST':
        form = IncidenteForm(request.POST, instance=incidente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incidente actualizado correctamente.')
            return redirect('lista_incidentes')
    else:
        form = IncidenteForm(instance=incidente)

    return render(
        request,
        'registrar_incidente.html',
        {'form': form, 'modo': 'editar', 'incidente': incidente},
    )


@login_required
def eliminar_incidente(request, id):
    incidente = get_object_or_404(Incidente, id=id)

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
            messages.success(request, 'Sesion iniciada correctamente.')
            return redirect(next_url or 'dashboard')

        return render(request, 'login.html', {'error': 'Usuario o contrasena incorrectos'})

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Sesion cerrada correctamente.')
    return redirect('login')


@login_required
def dashboard(request):
    incidentes = Incidente.objects.select_related('responsable', 'creado_por')
    total = incidentes.count()
    pendientes = incidentes.filter(estado='pendiente').count()
    en_proceso = incidentes.filter(estado='en_proceso').count()
    resueltos = incidentes.filter(estado='resuelto').count()
    criticos = incidentes.filter(riesgo='critico').count()
    incidentes_recientes = incidentes.order_by('-fecha', '-creado_en')[:5]

    contexto = {
        'total': total,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'resueltos': resueltos,
        'criticos': criticos,
        'incidentes_recientes': incidentes_recientes,
    }

    return render(request, 'dashboard.html', contexto)
