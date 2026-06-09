from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .models import Incidente
from .forms import IncidenteForm

# Create your views here.

def inicio(request):
    return render(request, 'inicio.html')

def registrar_incidente(request):
    if request.method == 'POST':
        form = IncidenteForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('lista_incidentes')
        else:
            print(form.errors)

    else:
        form = IncidenteForm()

    return render(request, 'registrar_incidente.html', {'form': form})

def lista_incidentes(request):
    incidentes = Incidente.objects.all().order_by('-fecha')
    return render(request, 'lista_incidentes.html', {'incidentes': incidentes})


def editar_incidente(request, id):
    incidente = get_object_or_404(Incidente, id=id)

    if request.method == 'POST':
        form = IncidenteForm(request.POST, instance=incidente)
        if form.is_valid():
            form.save()
            return redirect('lista_incidentes')
    else:
        form = IncidenteForm(instance=incidente)

    return render(request, 'registrar_incidente.html', {'form': form})

def eliminar_incidente(request, id):
    incidente = get_object_or_404(Incidente, id=id)
    if request.method == 'POST':
        incidente.delete()
        return redirect('lista_incidentes')   
    return render(request, 'confirmar_eliminar.html', {'incidente': incidente})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'login.html')

def dashboard(request):

    total = Incidente.objects.count()

    pendientes = Incidente.objects.filter(
        estado='pendiente'
    ).count()

    en_proceso = Incidente.objects.filter(
        estado='en_proceso'
    ).count()

    resueltos = Incidente.objects.filter(
        estado='resuelto'
    ).count()
    
    criticos = Incidente.objects.filter(
        riesgo='critico'
    ).count()

    incidentes_recientes = Incidente.objects.order_by('-fecha')[:5]

    contexto = {
        'total': total,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'resueltos': resueltos,
        'criticos': criticos,
        'incidentes_recientes': incidentes_recientes,
    }

    return render(
        request,
        'dashboard.html',
        contexto
    )