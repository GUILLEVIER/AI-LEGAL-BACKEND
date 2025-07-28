from django.contrib import admin
from .models import (
    Tribunales,
    DocumentoSubido,
    CampoDisponible,
    PlantillaDocumento,
    CampoPlantilla,
    DocumentoGenerado,
    PlantillaFavorita,
    TipoPlantillaDocumento,
    PlantillaCompartida,
    ClasificacionPlantillaGeneral,
    PlantillaGeneral,
)

from unfold.admin import ModelAdmin


@admin.register(Tribunales)
class TribunalesAdmin(ModelAdmin):
    pass

@admin.register(DocumentoSubido)
class DocumentoSubidoAdmin(ModelAdmin):
    list_display = ('nombre_original', 'tipo', 'usuario', 'fecha_subida')
    list_filter = ('tipo', 'fecha_subida')
    search_fields = ('nombre_original', 'usuario__username')

@admin.register(CampoDisponible)
class CampoDisponibleAdmin(ModelAdmin):
    list_display = ('nombre', 'tipo_dato')
    list_filter = ('tipo_dato',)
    search_fields = ('nombre',)

@admin.register(TipoPlantillaDocumento)
class TipoPlantillaDocumentoAdmin(ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(PlantillaDocumento)
class PlantillaDocumentoAdmin(ModelAdmin):
    list_display = ('nombre', 'usuario', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('nombre', 'usuario__username')
    readonly_fields = ('fecha_creacion',)

@admin.register(CampoPlantilla)
class CampoPlantillaAdmin(ModelAdmin):
    list_display = ('plantilla', 'campo', 'nombre_variable')
    list_filter = ('campo__tipo_dato',)
    search_fields = ('plantilla__nombre', 'campo__nombre', 'nombre_variable')

@admin.register(DocumentoGenerado)
class DocumentoGeneradoAdmin(ModelAdmin):
    list_display = ('plantilla', 'fecha_generacion')
    list_filter = ('fecha_generacion',)
    search_fields = ('plantilla__nombre',)
    readonly_fields = ('fecha_generacion',)

@admin.register(PlantillaFavorita)
class PlantillaFavoritaAdmin(ModelAdmin):
    list_display = ('usuario', 'plantilla', 'fecha_agregado')
    list_filter = ('fecha_agregado',)
    search_fields = ('usuario__username', 'plantilla__nombre')
    readonly_fields = ('fecha_agregado',)
    ordering = ('-fecha_agregado',)

@admin.register(PlantillaCompartida)
class PlantillaCompartidaAdmin(ModelAdmin):
    list_display = ('plantilla', 'usuario', 'permisos', 'fecha_compartida')
    search_fields = ('plantilla__nombre', 'usuario__username')
    list_filter = ('permisos',)

@admin.register(ClasificacionPlantillaGeneral)
class ClasificacionPlantillaGeneralAdmin(ModelAdmin):
    list_display = ('id', 'nombre', 'fecha_creacion', 'total_plantillas')
    search_fields = ('nombre',)
    list_filter = ('fecha_creacion',)
    readonly_fields = ('fecha_creacion',)
    ordering = ('-fecha_creacion',)
    
    def total_plantillas(self, obj):
        """Muestra el número total de plantillas generales asociadas"""
        return obj.plantillageneral_set.count()
    total_plantillas.short_description = 'Total Plantillas'
    total_plantillas.admin_order_field = 'plantillageneral_count'
    
    def get_queryset(self, request):
        """Optimiza las consultas agregando el conteo de plantillas"""
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('plantillageneral_set')
        return queryset

@admin.register(PlantillaGeneral)
class PlantillaGeneralAdmin(ModelAdmin):
    list_display = ('id', 'nombre', 'clasificacion', 'total_documentos', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion', 'clasificacion__nombre')
    list_filter = ('clasificacion', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)
    ordering = ('-fecha_creacion',)
    filter_horizontal = ('documentos',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'clasificacion', 'descripcion')
        }),
        ('Documentos Asociados', {
            'fields': ('documentos',),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def total_documentos(self, obj):
        """Muestra el número total de documentos asociados"""
        return obj.documentos.count()
    total_documentos.short_description = 'Total Documentos'
    total_documentos.admin_order_field = 'documentos_count'
    
    def get_queryset(self, request):
        """Optimiza las consultas con select_related y prefetch_related"""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('clasificacion').prefetch_related('documentos')
        return queryset

