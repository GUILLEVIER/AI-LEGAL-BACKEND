from django.contrib import admin
from .models import (
    Tribunales, TipoDocumento, Documentos, Favoritos, Compartir, Escritos, Demandas, Contratos, Clasificacion, Plantillas
)

from unfold.admin import ModelAdmin


@admin.register(Tribunales)
class TribunalesAdmin(ModelAdmin):
    pass

@admin.register(TipoDocumento)
class TipoDocumentoAdmin(ModelAdmin):
    pass

@admin.register(Documentos)
class DocumentosAdmin(ModelAdmin):
    pass

@admin.register(Favoritos)
class FavoritosAdmin(ModelAdmin):
    pass

@admin.register(Compartir)
class CompartirAdmin(ModelAdmin):
    pass

@admin.register(Escritos)
class EscritosAdmin(ModelAdmin):
    pass

@admin.register(Demandas)
class DemandasAdmin(ModelAdmin):
    pass

@admin.register(Contratos)
class ContratosAdmin(ModelAdmin):
    pass

@admin.register(Clasificacion)
class ClasificacionAdmin(ModelAdmin):
    pass

@admin.register(Plantillas)
class PlantillasAdmin(ModelAdmin):
    pass
