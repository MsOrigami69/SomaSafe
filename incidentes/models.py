from django.db import models

# Create your models here.
class Incidente(models.Model):
    TIPOS_INCIDENTE = [
        ('accidente', 'Accidente'),
        ('casi_accidente', 'Casi accidente'),
        ('condicion_insegura', 'Condición insegura'),
    ]

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('resuelto', 'Resuelto'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS_INCIDENTE)
    fecha = models.DateField()
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=150)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)

def __str__(self):
  return f"{self.tipo} - {self.fecha} - {self.ubicacion}"