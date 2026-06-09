from django import forms
from .models import Incidente
from datetime import date

class IncidenteForm(forms.ModelForm):

    riesgo = forms.ChoiceField(
        choices=Incidente.NIVEL_RIESGO,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Nivel de riesgo'
    )

    class Meta:
        model = Incidente
        fields = [
            'tipo',
            'fecha',
            'descripcion',
            'ubicacion',
            'estado',
            'riesgo'
        ]

        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')

        if fecha and fecha > date.today():
            raise forms.ValidationError(
                "La fecha no puede ser futura."
            )

        return fecha

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')

        if descripcion and len(descripcion.strip()) < 10:
            raise forms.ValidationError(
                "La descripción es muy corta."
            )

        return descripcion