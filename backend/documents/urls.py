from django.urls import path
from .views import (
    TipoDocumentoListAPIView, DocumentosListAPIView, FavoritosListAPIView, CompartirListAPIView,
    EscritosListAPIView, DemandasListAPIView, ContratosListAPIView,
    ClasificacionListAPIView, PlantillasListAPIView
)

urlpatterns = [
    path('tipodocumento/', TipoDocumentoListAPIView.as_view(), name='tipodocumento-list'),
    path('documentos/', DocumentosListAPIView.as_view(), name='documentos-list'),
    path('favoritos/', FavoritosListAPIView.as_view(), name='favoritos-list'),
    path('compartir/', CompartirListAPIView.as_view(), name='compartir-list'),
    path('escritos/', EscritosListAPIView.as_view(), name='escritos-list'),
    path('demandas/', DemandasListAPIView.as_view(), name='demandas-list'),
    path('contratos/', ContratosListAPIView.as_view(), name='contratos-list'),
    path('clasificacion/', ClasificacionListAPIView.as_view(), name='clasificacion-list'),
    path('plantillas/', PlantillasListAPIView.as_view(), name='plantillas-list'),
]