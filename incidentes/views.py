from django.shortcuts import render, redirect, get_object_or_404
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
    incidente.delete()
    return redirect('lista_incidentes')   

from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('lista_incidentes')
        else:
            return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'login.html')