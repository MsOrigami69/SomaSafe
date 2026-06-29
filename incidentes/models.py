from django.conf import settings
from django.db import models


class Incidente(models.Model):
    TIPOS_INCIDENTE = [
        ('accidente', 'Accidente'),
        ('casi_accidente', 'Casi accidente'),
        ('condicion_insegura', 'Condicion insegura'),
    ]

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('resuelto', 'Resuelto'),
    ]

    NIVEL_RIESGO = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
        ('critico', 'Critico'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS_INCIDENTE)
    fecha = models.DateField()
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=150)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    riesgo = models.CharField(max_length=10, choices=NIVEL_RIESGO, default='bajo')
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidentes_asignados',
    )
    acciones_correctivas = models.TextField(blank=True)
    fecha_resolucion = models.DateField(null=True, blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidentes_creados',
        editable=False,
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha} - {self.ubicacion}"
