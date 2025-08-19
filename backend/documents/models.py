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
    html = models.TextField(blank=True, null=True)
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
        db_table = 'tipos_plantillas_documentos'
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
    nombre = models.CharField(max_length=255)
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
        managed = True
        db_table = 'plantillas_favoritas'
        verbose_name_plural = 'Plantillas Favoritas'
        unique_together = ['usuario', 'plantilla']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.plantilla.nombre}"

class PlantillaCompartida(models.Model):
    plantilla = models.ForeignKey('PlantillaDocumento', on_delete=models.CASCADE, related_name='compartidas')
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='plantillas_compartidas')
    permisos = models.CharField(max_length=20, choices=[('lectura', 'Solo lectura'), ('edicion', 'Lectura y edición')], default='lectura')
    fecha_compartida = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'plantillas_compartidas'
        verbose_name_plural = 'Plantillas Compartidas'
        unique_together = ('plantilla', 'usuario')

    def __str__(self):
        return f"{self.plantilla.nombre} → {self.usuario.username} ({self.permisos})"

class ClasificacionPlantillaGeneral(models.Model):
    """
    Categorías para organizar los paquetes de plantillas.
    Ejemplos: "Contratos Comerciales", "Documentos Laborales", "Societario", etc.
    """
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(
        max_length=200, 
        blank=False, 
        null=False,
        help_text="Nombre de la categoría (ej: 'Contratos Comerciales')"
    )
    descripcion = models.TextField(
        blank=True, 
        null=True,
        help_text="Descripción de qué tipo de paquetes incluye esta categoría"
    )
    
    # Control administrativo
    creado_por = models.ForeignKey(
        Usuarios,
        on_delete=models.CASCADE,
        related_name='clasificaciones_paquetes_creadas',
        help_text="Administrador que creó esta clasificación"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'clasificaciones_plantillas_generales'
        verbose_name = 'Categoría de Paquetes'
        verbose_name_plural = 'Categorías de Paquetes'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['creado_por']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.get_paquetes_count()} paquetes)"
    
    def get_paquetes_count(self):
        """Retorna el número de paquetes en esta categoría"""
        return self.plantillageneral_set.filter(activo=True).count()
    
    def get_paquetes_activos(self):
        """Retorna los paquetes activos de esta categoría"""
        return self.plantillageneral_set.filter(activo=True).order_by('nombre')
    
    def get_total_plantillas_en_categoria(self):
        """Retorna el total de plantillas en todos los paquetes de esta categoría"""
        from django.db.models import Count
        return self.plantillageneral_set.filter(activo=True).aggregate(
            total=Count('plantillas_incluidas', distinct=True)
        )['total'] or 0


class PlantillaGeneral(models.Model):
    """
    Paquete de plantillas creado por administradores.
    Agrupa múltiples PlantillaDocumento para otorgar acceso conjunto a usuarios/empresas.
    """
    
    id = models.AutoField(primary_key=True)
    clasificacion = models.ForeignKey(ClasificacionPlantillaGeneral, null=False, blank=False, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200, blank=False, null=False, 
                            help_text="Nombre del paquete de plantillas")
    descripcion = models.TextField(blank=True, null=True, 
                                 help_text="Descripción del paquete y qué plantillas incluye")
    
    # Plantillas incluidas en este paquete
    plantillas_incluidas = models.ManyToManyField(
        PlantillaDocumento, 
        blank=True,
        help_text="Plantillas de documento incluidas en este paquete",
        related_name='paquetes_que_la_incluyen'
    )
    
    # Control de administración
    creado_por_admin = models.ForeignKey(
        Usuarios, 
        on_delete=models.CASCADE, 
        related_name='paquetes_plantillas_creados',
        help_text="Administrador que creó este paquete"
    )
    
    # Estado del paquete
    activo = models.BooleanField(default=True, help_text="Si el paquete está disponible para asignar")
    es_paquete_premium = models.BooleanField(default=False, 
                                           help_text="Si es un paquete premium con plantillas especiales")

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'plantillas_generales'
        verbose_name = 'Paquete de Plantillas'
        verbose_name_plural = 'Paquetes de Plantillas'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['activo']),
            models.Index(fields=['creado_por_admin']),
            models.Index(fields=['clasificacion', 'activo']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.get_total_plantillas()} plantillas)"
    
    def get_total_plantillas(self):
        """Retorna el número total de plantillas incluidas en este paquete"""
        return self.plantillas_incluidas.count()
    
    def get_plantillas_por_categoria(self):
        """Retorna las plantillas agrupadas por tipo"""
        from collections import defaultdict
        plantillas_por_tipo = defaultdict(list)
        
        for plantilla in self.plantillas_incluidas.select_related('tipo'):
            tipo_nombre = plantilla.tipo.nombre if plantilla.tipo else 'Sin tipo'
            plantilla_data = {
                'id': plantilla.id,
                'nombre': plantilla.nombre,
                'descripcion': plantilla.descripcion,
                'tipo': {
                    'id': plantilla.tipo.id,
                    'nombre': plantilla.tipo.nombre
                } if plantilla.tipo else None
            }
            plantillas_por_tipo[tipo_nombre].append(plantilla_data)
            
        return dict(plantillas_por_tipo)
    
    def get_plantillas_por_clasificacion(self):
        """Retorna información de la clasificación y las plantillas incluidas en este paquete"""
        return {
            'clasificacion': {
                'id': self.clasificacion.id,
                'nombre': self.clasificacion.nombre,
                'descripcion': self.clasificacion.descripcion,
                'creado_por': self.clasificacion.creado_por.get_full_name() or self.clasificacion.creado_por.username,
                'fecha_creacion': self.clasificacion.fecha_creacion.isoformat() if self.clasificacion.fecha_creacion else None,
            },
            'paquete': {
                'id': self.id,
                'nombre': self.nombre,
                'descripcion': self.descripcion,
                'total_plantillas': self.get_total_plantillas(),
                'es_premium': self.es_paquete_premium,
                'activo': self.activo,
            },
            'plantillas': list(self.plantillas_incluidas.values(
                'id', 'nombre', 'descripcion', 'tipo__nombre'
            ))
        }
    
    def puede_ser_asignado_a_usuario(self, usuario):
        """Verifica si este paquete puede ser asignado a un usuario específico"""
        if not self.activo:
            return False
            
        # Verificar si el usuario ya tiene acceso a este paquete
        return not PlantillaGeneralCompartida.objects.filter(
            plantilla_general=self,
            usuario=usuario,
            activo=True
        ).exists()
    
    def asignar_a_usuario(self, usuario, asignado_por, fecha_expiracion=None, notas=None):
        """Asigna este paquete de plantillas a un usuario específico"""
        if not self.puede_ser_asignado_a_usuario(usuario):
            return None
            
        asignacion, created = PlantillaGeneralCompartida.objects.get_or_create(
            plantilla_general=self,
            usuario=usuario,
            defaults={
                'asignado_por': asignado_por,
                'fecha_expiracion': fecha_expiracion,
                'notas': notas,
                'activo': True
            }
        )
        
        if not created and not asignacion.activo:
            # Reactivar asignación existente
            asignacion.activo = True
            asignacion.asignado_por = asignado_por
            asignacion.fecha_expiracion = fecha_expiracion
            asignacion.notas = notas
            asignacion.save()
            
        return asignacion
    
    def get_usuarios_con_acceso(self):
        """Obtiene todos los usuarios que tienen acceso a este paquete"""
        return Usuarios.objects.filter(
            plantillas_generales_asignadas__plantilla_general=self,
            plantillas_generales_asignadas__activo=True
        ).distinct()


class PlantillaGeneralCompartida(models.Model):
    """
    Asignación de paquetes de plantillas a usuarios específicos.
    Controla qué usuarios tienen acceso a qué paquetes de plantillas.
    """
    plantilla_general = models.ForeignKey(
        PlantillaGeneral, 
        on_delete=models.CASCADE, 
        related_name='asignaciones'
    )
    usuario = models.ForeignKey(
        Usuarios, 
        on_delete=models.CASCADE, 
        related_name='plantillas_generales_asignadas'
    )
    asignado_por = models.ForeignKey(
        Usuarios, 
        on_delete=models.CASCADE, 
        related_name='paquetes_plantillas_asignados',
        help_text="Administrador que asignó este paquete"
    )
    
    # Control de acceso
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(
        null=True, blank=True, 
        help_text="Fecha de expiración del acceso al paquete"
    )
    activo = models.BooleanField(default=True, help_text="Si la asignación está activa")
    
    # Metadatos
    notas = models.TextField(
        blank=True, null=True, 
        help_text="Notas sobre por qué se asignó este paquete"
    )
    fecha_ultimo_acceso = models.DateTimeField(
        null=True, blank=True,
        help_text="Última vez que el usuario accedió a plantillas de este paquete"
    )
    
    class Meta:
        db_table = 'plantillas_generales_compartidas'
        unique_together = ['plantilla_general', 'usuario']
        indexes = [
            models.Index(fields=['plantilla_general', 'usuario', 'activo']),
            models.Index(fields=['fecha_expiracion']),
            models.Index(fields=['asignado_por']),
        ]
        verbose_name = "Asignación de Paquete de Plantillas"
        verbose_name_plural = "Asignaciones de Paquetes de Plantillas"
        
    def __str__(self):
        return f"Paquete '{self.plantilla_general.nombre}' → {self.usuario.get_full_name() or self.usuario.username}"
    
    def esta_vigente(self):
        """Verifica si la asignación está vigente"""
        if not self.activo:
            return False
        if self.fecha_expiracion and timezone.now() > self.fecha_expiracion:
            return False
        return True
    
    def marcar_acceso(self):
        """Marca que el usuario accedió recientemente a plantillas de este paquete"""
        self.fecha_ultimo_acceso = timezone.now()
        self.save(update_fields=['fecha_ultimo_acceso'])
    
    def get_plantillas_disponibles(self):
        """Retorna las plantillas disponibles en este paquete"""
        if not self.esta_vigente():
            return PlantillaDocumento.objects.none()
        return self.plantilla_general.plantillas_incluidas.all()