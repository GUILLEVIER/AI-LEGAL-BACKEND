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
    CategoriaPlantillaDocumento,
    PlantillaCompartida,
    ClasificacionPlantillaGeneral,
    PlantillaGeneral,
    PlantillaGeneralCompartida,
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

@admin.register(CategoriaPlantillaDocumento)
class CategoriaPlantillaDocumentoAdmin(ModelAdmin):
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
    list_display = ('id', 'nombre', 'clasificacion', 'total_plantillas', 'activo', 'es_paquete_premium', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion', 'clasificacion__nombre')
    list_filter = ('clasificacion', 'activo', 'es_paquete_premium', 'fecha_creacion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ('-fecha_creacion',)
    filter_horizontal = ('plantillas_incluidas',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'clasificacion', 'descripcion')
        }),
        ('Configuración del Paquete', {
            'fields': ('activo', 'es_paquete_premium', 'creado_por_admin')
        }),
        ('Plantillas Incluidas', {
            'fields': ('plantillas_incluidas',),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def total_plantillas(self, obj):
        """Muestra el número total de plantillas incluidas en el paquete"""
        return obj.get_total_plantillas()
    total_plantillas.short_description = 'Total Plantillas'
    total_plantillas.admin_order_field = 'plantillas_count'
    
    def get_queryset(self, request):
        """Optimiza las consultas con select_related y prefetch_related"""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('clasificacion', 'creado_por_admin').prefetch_related('plantillas_incluidas')
        return queryset

@admin.register(PlantillaGeneralCompartida)
class PlantillaGeneralCompartidaAdmin(ModelAdmin):
    list_display = ('plantilla_general', 'usuario', 'asignado_por', 'activo', 'esta_vigente_display', 'fecha_asignacion')
    search_fields = ('plantilla_general__nombre', 'usuario__username', 'usuario__first_name', 'usuario__last_name')
    list_filter = ('activo', 'fecha_asignacion', 'fecha_expiracion', 'plantilla_general__clasificacion')
    readonly_fields = ('fecha_asignacion', 'fecha_ultimo_acceso')
    ordering = ('-fecha_asignacion',)
    
    fieldsets = (
        ('Asignación', {
            'fields': ('plantilla_general', 'usuario', 'asignado_por')
        }),
        ('Control de Acceso', {
            'fields': ('activo', 'fecha_expiracion', 'notas')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_asignacion', 'fecha_ultimo_acceso'),
            'classes': ('collapse',)
        }),
    )
    
    def esta_vigente_display(self, obj):
        """Muestra si la asignación está vigente"""
        return obj.esta_vigente()
    esta_vigente_display.short_description = 'Vigente'
    esta_vigente_display.boolean = True
    
    def get_queryset(self, request):
        """Optimiza las consultas con select_related"""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('plantilla_general', 'usuario', 'asignado_por', 'plantilla_general__clasificacion')
        return queryset

