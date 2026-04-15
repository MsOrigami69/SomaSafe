from django import forms
from .models import Incidente


class IncidenteForm(forms.ModelForm):
    class Meta:
        model = Incidente
        fields = ['tipo', 'fecha', 'descripcion', 'ubicacion', 'estado']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'tipo': 'Tipo de incidente',
            'fecha': 'Fecha',
            'descripcion': 'Descripción',
            'ubicacion': 'Ubicación',
            'estado': 'Estado',
        }