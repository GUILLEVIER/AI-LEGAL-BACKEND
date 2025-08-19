from django.urls import path, include
from .views import EmpresasViewSet, EmpresasListAPIView, PlanesListAPIView, TribunalesListAPIView #TribunalesViewset #TribunalesListAPIView, TribunalesDetailAPIView,

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('empresas', EmpresasViewSet, basename='empresas')

urlpatterns = [
    path('empresas/', EmpresasListAPIView.as_view(), name='empresas-list'),
    path('planes/', PlanesListAPIView.as_view(), name='planes-list'),
    path('tribunales/', TribunalesListAPIView.as_view(), name='tribunales-list'),

    # generics
    #path('tribunales/', TribunalesListAPIView.as_view(), name='tribunales-list'),
    #path('tribunales/<int:pk>/', TribunalesDetailAPIView.as_view(), name='tribunales-detail'),

    # viewset
    #path('', include(router.urls))
]