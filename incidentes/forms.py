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
            'evidencia',
            'consecuencias',
            'observaciones',
            'prioridad',
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describa detalladamente qué sucedió...'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Nivel 3, Galería Norte'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'riesgo': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'acciones_correctivas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Medidas inmediatas adoptadas...'}),
            'fecha_resolucion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'evidencia': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'consecuencias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Impacto operacional, ambiental o daños personales...'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales relevantes...'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'riesgo': 'Nivel de riesgo',
            'fecha_resolucion': 'Fecha de resolución',
            'acciones_correctivas': 'Acciones correctivas',
            'evidencia': 'Evidencia fotográfica',
            'consecuencias': 'Consecuencias del incidente',
            'observaciones': 'Observaciones adicionales',
            'prioridad': 'Prioridad',
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
