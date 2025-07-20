from django.contrib import admin
from .models import (
    DocumentoSubido,
    CampoDisponible,
    PlantillaDocumento,
    CampoPlantilla,
    DocumentoGenerado,
    FavoritoPlantilla,
    TipoPlantillaDocumento,
    PlantillaCompartida
)

@admin.register(DocumentoSubido)
class DocumentoSubidoAdmin(admin.ModelAdmin):
    list_display = ('nombre_original', 'tipo', 'usuario', 'fecha_subida')
    list_filter = ('tipo', 'fecha_subida')
    search_fields = ('nombre_original', 'usuario__username')

@admin.register(CampoDisponible)
class CampoDisponibleAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_dato')
    list_filter = ('tipo_dato',)
    search_fields = ('nombre',)

@admin.register(TipoPlantillaDocumento)
class TipoPlantillaDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(PlantillaDocumento)
class PlantillaDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('nombre', 'usuario__username')
    readonly_fields = ('fecha_creacion',)

@admin.register(CampoPlantilla)
class CampoPlantillaAdmin(admin.ModelAdmin):
    list_display = ('plantilla', 'campo', 'nombre_variable')
    list_filter = ('campo__tipo_dato',)
    search_fields = ('plantilla__nombre', 'campo__nombre', 'nombre_variable')

@admin.register(DocumentoGenerado)
class DocumentoGeneradoAdmin(admin.ModelAdmin):
    list_display = ('plantilla', 'fecha_generacion')
    list_filter = ('fecha_generacion',)
    search_fields = ('plantilla__nombre',)
    readonly_fields = ('fecha_generacion',)

@admin.register(FavoritoPlantilla)
class FavoritoPlantillaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'plantilla', 'fecha_agregado')
    list_filter = ('fecha_agregado',)
    search_fields = ('usuario__username', 'plantilla__nombre')
    readonly_fields = ('fecha_agregado',)
    ordering = ('-fecha_agregado',)

@admin.register(PlantillaCompartida)
class PlantillaCompartidaAdmin(admin.ModelAdmin):
    list_display = ('plantilla', 'usuario', 'permisos', 'fecha_compartida')
    search_fields = ('plantilla__nombre', 'usuario__username')
    list_filter = ('permisos',)
