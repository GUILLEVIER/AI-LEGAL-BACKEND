from django.contrib import admin
from .models import (
    Tribunales, TipoDocumento, Documentos, Favoritos, Compartir, Escritos, Demandas, Contratos, Clasificacion, Plantillas
)

admin.site.register(Tribunales)
admin.site.register(TipoDocumento)
admin.site.register(Documentos)
admin.site.register(Favoritos)
admin.site.register(Compartir)
admin.site.register(Escritos)
admin.site.register(Demandas)
admin.site.register(Contratos)
admin.site.register(Clasificacion)
admin.site.register(Plantillas)
