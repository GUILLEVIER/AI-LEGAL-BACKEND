from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentoSubidoViewSet,
    CampoDisponibleViewSet,
    PlantillaDocumentoViewSet,
    DocumentoGeneradoViewSet,
    PlantillaFavoritaViewSet, TipoPlantillaDocumentoListAPIView,
    #TipoPlantillaDocumentoViewSet,
    PlantillaCompartidaViewSet,
    CategoriaPlantillaDocumentoListAPIView, 
    #ClasificacionPlantillaGeneralViewSet,
    PlantillaGeneralViewSet,
    ClasificacionPlantillaGeneralListAPIView,
    PlantillaGeneralCompartidaViewSet,
    UsuariosViewSet,
)

router = DefaultRouter()
router.register(r'documentos-subidos', DocumentoSubidoViewSet)
router.register(r'campos-disponibles', CampoDisponibleViewSet)
#outer.register(r'tipos-plantilla', TipoPlantillaDocumentoViewSet)
router.register(r'plantillas-documentos', PlantillaDocumentoViewSet)
router.register(r'documentos-generados', DocumentoGeneradoViewSet)
router.register(r'plantillas-favoritas', PlantillaFavoritaViewSet)
router.register(r'plantillas-compartidas', PlantillaCompartidaViewSet)
#router.register(r'clasificacion-plantillas-generales', ClasificacionPlantillaGeneralViewSet)
router.register(r'plantilla-generales', PlantillaGeneralViewSet)
router.register(r'plantillas-generales-compartidas', PlantillaGeneralCompartidaViewSet)
#router.register(r'usuarios', UsuariosViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('tipos-plantilla/', TipoPlantillaDocumentoListAPIView.as_view(), name='tipos-plantilla-list'),
    path('clasificacion-plantillas-generales/', ClasificacionPlantillaGeneralListAPIView.as_view(), name='clasificacion-plantillas-generales-list'),
    path('categorias-plantilla/', CategoriaPlantillaDocumentoListAPIView.as_view(), name='categorias-plantilla-list'),
]