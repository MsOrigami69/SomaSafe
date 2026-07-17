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
    consecuencias = models.TextField(blank=True, verbose_name='Consecuencias del incidente')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones adicionales')
    prioridad = models.CharField(
        max_length=15,
        choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta'), ('urgente', 'Urgente')],
        default='baja',
        verbose_name='Prioridad'
    )
    evidencia = models.ImageField(
        upload_to='incidentes/evidencias/',
        blank=True,
        null=True,
        verbose_name='Evidencia fotográfica'
    )
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


class HistorialIncidente(models.Model):
    """Modelo para Auditoría (Audit Trail) de cambios"""
    incidente = models.ForeignKey(Incidente, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    campo_modificado = models.CharField(max_length=100)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_nuevo = models.TextField(blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_cambio']

    def __str__(self):
        return f"Cambio en #{self.incidente.id} por {self.usuario} el {self.fecha_cambio}"
