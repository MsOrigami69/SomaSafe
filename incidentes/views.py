from django.shortcuts import render, redirect
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
            return redirect('inicio')
    else:
        form = IncidenteForm()

    return render(request, 'registrar_incidente.html', {'form': form})