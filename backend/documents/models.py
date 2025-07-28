from django.db import models
from users.models import Usuarios
from companies.models import Empresas
from companies.models import Tribunales
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
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    nombre_original = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    archivo_url = models.CharField(max_length=500)
    fecha_subida = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'documentos_subidos'
        verbose_name_plural = 'Documentos Subidos'
    
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

    class Meta:
        managed = True
        db_table = 'campos_disponibles'
        verbose_name_plural = 'Campos Disponibles'
    
    def __str__(self):
        return f"{self.nombre} ({self.tipo_dato})"

class TipoPlantillaDocumento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = True
        db_table = 'tipos_plantillas'
        verbose_name_plural = 'Tipos de Plantillas'
    
    def __str__(self):
        return self.nombre

class PlantillaDocumento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    html_con_campos = models.TextField()
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoPlantillaDocumento, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'plantillas_documentos'
        verbose_name_plural = 'Plantillas de Documentos'
    
    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"

class CampoPlantilla(models.Model):
    id = models.AutoField(primary_key=True)
    plantilla = models.ForeignKey(PlantillaDocumento, on_delete=models.CASCADE, related_name='campos_asociados')
    campo = models.ForeignKey(CampoDisponible, on_delete=models.CASCADE)
    nombre_variable = models.CharField(max_length=100)  # {{rut}}, etc.
    
    class Meta:
        managed = True
        db_table = 'campos_plantillas'
        verbose_name_plural = 'Campos de Plantillas'

    def __str__(self):
        return f"{self.nombre_variable} -> {self.campo.nombre}"

class DocumentoGenerado(models.Model):
    id = models.AutoField(primary_key=True)
    plantilla = models.ForeignKey(PlantillaDocumento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    datos_rellenados = models.JSONField()
    html_resultante = models.TextField()
    fecha_generacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'documentos_generados'
        verbose_name_plural = 'Documentos Generados'
    
    def __str__(self):
        return f"Documento generado de {self.plantilla.nombre} por {self.usuario.username} - {self.fecha_generacion}"
    
    def get_datos_rellenados(self):
        if isinstance(self.datos_rellenados, str):
            return json.loads(self.datos_rellenados)
        return self.datos_rellenados

class PlantillaFavorita(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    plantilla = models.ForeignKey(PlantillaDocumento, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['usuario', 'plantilla']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.plantilla.nombre}"

class PlantillaCompartida(models.Model):
    plantilla = models.ForeignKey('PlantillaDocumento', on_delete=models.CASCADE, related_name='compartidas')
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='plantillas_compartidas')
    permisos = models.CharField(max_length=20, choices=[('lectura', 'Solo lectura'), ('edicion', 'Lectura y edición')], default='lectura')
    fecha_compartida = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('plantilla', 'usuario')

    def __str__(self):
        return f"{self.plantilla.nombre} → {self.usuario.username} ({self.permisos})"

class ClasificacionPlantillaGeneral(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, blank=False, null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'clasificacion_plantilla_general'
        verbose_name_plural = 'Clasificacion Plantilla General'

    def __str__(self):
        txt = "{0}"
        return txt.format(self.nombre)

class PlantillaGeneral(models.Model):
    id = models.AutoField(primary_key=True)
    clasificacion = models.ForeignKey(ClasificacionPlantillaGeneral, null=False, blank=False, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200, blank=False, null=False)
    descripcion = models.CharField(max_length=1000, blank=True, null=True)
    documentos = models.ManyToManyField(PlantillaDocumento, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'plantillas_generales'
        verbose_name_plural = 'Plantillas Generales'

    def __str__(self):
        txt = "{0}"
        return txt.format(self.nombre)
