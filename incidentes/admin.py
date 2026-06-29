from django.contrib import admin
from .models import Incidente


@admin.register(Incidente)
class IncidenteAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'fecha', 'ubicacion', 'estado', 'riesgo', 'creado_en')
    list_filter = ('tipo', 'estado', 'riesgo')
    search_fields = ('descripcion', 'ubicacion')
