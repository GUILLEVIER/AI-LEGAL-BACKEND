from django.urls import path, include
from .views import EmpresasListAPIView, PlanesListAPIView, TribunalesViewset #TribunalesListAPIView, TribunalesDetailAPIView,

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('tribunales', TribunalesViewset, basename='tribunal')

urlpatterns = [
    path('empresas/', EmpresasListAPIView.as_view(), name='empresas-list'),
    path('planes/', PlanesListAPIView.as_view(), name='planes-list'),

    # generics
    #path('tribunales/', TribunalesListAPIView.as_view(), name='tribunales-list'),
    #path('tribunales/<int:pk>/', TribunalesDetailAPIView.as_view(), name='tribunales-detail'),

    # viewset
    path('', include(router.urls))
]