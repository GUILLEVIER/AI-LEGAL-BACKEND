from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class DocumentoSubido(models.Model):
    TIPO_CHOICES = [
        ('pdf', 'PDF'),
        ('imagen', 'Imagen'),
        ('texto', 'Texto'),
        ('word', 'Docx'),
    ]
    
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_original = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    archivo_url = models.CharField(max_length=500)
    fecha_subida = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.nombre_original} - {self.usuario.username}"

class CampoDisponible(models.Model):
    TIPO_DATO_CHOICES = [
        ('texto', 'Texto'),
        ('fecha', 'Fecha'),
        ('numero', 'Número'),
    ]
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    tipo_dato = models.CharField(max_length=10, choices=TIPO_DATO_CHOICES)
    
    def __str__(self):
        return f"{self.nombre} ({self.tipo_dato})"

class TipoPlantillaDocumento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre

class PlantillaDocumento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    html_con_campos = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoPlantillaDocumento, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"

class CampoPlantilla(models.Model):
    id = models.AutoField(primary_key=True)
    plantilla = models.ForeignKey(PlantillaDocumento, on_delete=models.CASCADE, related_name='campos_asociados')
    campo = models.ForeignKey(CampoDisponible, on_delete=models.CASCADE)
    nombre_variable = models.CharField(max_length=100)  # {{nombre_cliente}}, etc.
    
    def __str__(self):
        return f"{self.nombre_variable} -> {self.campo.nombre}"

class DocumentoGenerado(models.Model):
    id = models.AutoField(primary_key=True)
    plantilla = models.ForeignKey(PlantillaDocumento, on_delete=models.CASCADE)
    datos_rellenados = models.JSONField()
    html_resultante = models.TextField()
    fecha_generacion = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Documento generado de {self.plantilla.nombre} - {self.fecha_generacion}"
    
    def get_datos_rellenados(self):
        if isinstance(self.datos_rellenados, str):
            return json.loads(self.datos_rellenados)
        return self.datos_rellenados

class FavoritoPlantilla(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    plantilla = models.ForeignKey(PlantillaDocumento, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['usuario', 'plantilla']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.plantilla.nombre}"

class PlantillaCompartida(models.Model):
    plantilla = models.ForeignKey('PlantillaDocumento', on_delete=models.CASCADE, related_name='compartidas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plantillas_compartidas')
    permisos = models.CharField(max_length=20, choices=[('lectura', 'Solo lectura'), ('edicion', 'Lectura y edición')], default='lectura')
    fecha_compartida = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('plantilla', 'usuario')

    def __str__(self):
        return f"{self.plantilla.nombre} → {self.usuario.username} ({self.permisos})"
