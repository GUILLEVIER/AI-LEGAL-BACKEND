from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentoSubidoViewSet,
    CampoDisponibleViewSet,
    PlantillaDocumentoViewSet,
    DocumentoGeneradoViewSet,
    FavoritoPlantillaViewSet,
    TipoPlantillaDocumentoViewSet,
    PlantillaCompartidaViewSet,
    listar_usuarios,
)

router = DefaultRouter()
router.register(r'documentos-subidos', DocumentoSubidoViewSet)
router.register(r'campos-disponibles', CampoDisponibleViewSet)
router.register(r'tipos-plantilla', TipoPlantillaDocumentoViewSet)
router.register(r'plantillas', PlantillaDocumentoViewSet)
router.register(r'documentos-generados', DocumentoGeneradoViewSet)
router.register(r'favoritos', FavoritoPlantillaViewSet)
router.register(r'compartidas', PlantillaCompartidaViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/usuarios/', listar_usuarios, name='listar_usuarios'),
]