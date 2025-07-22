from django.urls import path
from .views import (
    TipoDocumentoListAPIView, DocumentosListAPIView, FavoritosListAPIView, CompartirListAPIView,
    EscritosListAPIView, DemandasListAPIView, ContratosListAPIView, ClasificacionListAPIView,
    PlantillasListAPIView, ConvertDocxToHtmlView, ConvertImageToHtmlView, ConvertPdfToHtmlView
)

urlpatterns = [
    #path('tipodocumento/', TipoDocumentoListAPIView.as_view(), name='tipodocumento-list'),
    path('documentos/', DocumentosListAPIView.as_view(), name='documentos-list'),
    #path('favoritos/', FavoritosListAPIView.as_view(), name='favoritos-list'),
    #path('compartir/', CompartirListAPIView.as_view(), name='compartir-list'),
    #path('escritos/', EscritosListAPIView.as_view(), name='escritos-list'),
    #path('demandas/', DemandasListAPIView.as_view(), name='demandas-list'),
    #path('contratos/', ContratosListAPIView.as_view(), name='contratos-list'),
    #path('clasificacion/', ClasificacionListAPIView.as_view(), name='clasificacion-list'),
    #path('plantillas/', PlantillasListAPIView.as_view(), name='plantillas-list'),
    path('docx_to_html/', ConvertDocxToHtmlView.as_view(), name='docx_to_html'),
    path('image_to_html/', ConvertImageToHtmlView.as_view(), name='image_to_html'),
    path('pdf_to_html/', ConvertPdfToHtmlView.as_view(), name='pdf_to_html'),
]