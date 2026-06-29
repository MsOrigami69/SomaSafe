from datetime import date

from django import forms

from .models import Incidente


class IncidenteForm(forms.ModelForm):
    class Meta:
        model = Incidente
        fields = [
            'tipo',
            'fecha',
            'descripcion',
            'ubicacion',
            'estado',
            'riesgo',
            'responsable',
            'acciones_correctivas',
            'fecha_resolucion',
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'riesgo': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'acciones_correctivas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'fecha_resolucion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'riesgo': 'Nivel de riesgo',
            'fecha_resolucion': 'Fecha de resolucion',
            'acciones_correctivas': 'Acciones correctivas',
        }

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')

        if fecha and fecha > date.today():
            raise forms.ValidationError('La fecha no puede ser futura.')

        return fecha

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')

        if descripcion and len(descripcion.strip()) < 10:
            raise forms.ValidationError('La descripcion es muy corta.')

        return descripcion

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        fecha_resolucion = cleaned_data.get('fecha_resolucion')

        if fecha_resolucion and fecha_resolucion > date.today():
            self.add_error('fecha_resolucion', 'La fecha de resolucion no puede ser futura.')

        if estado == 'resuelto' and not fecha_resolucion:
            self.add_error('fecha_resolucion', 'Debes indicar la fecha de resolucion.')

        return cleaned_data
