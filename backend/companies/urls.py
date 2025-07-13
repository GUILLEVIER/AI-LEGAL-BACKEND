from django.urls import path
from .views import EmpresasListAPIView, PlanesListAPIView, TribunalesListAPIView, TribunalesDetailAPIView

urlpatterns = [
    path('empresas/', EmpresasListAPIView.as_view(), name='empresas-list'),
    path('planes/', PlanesListAPIView.as_view(), name='planes-list'),
    path('tribunales/', TribunalesListAPIView.as_view(), name='tribunales-list'),
    path('tribunales/<int:pk>/', TribunalesDetailAPIView.as_view(), name='tribunales-detail'),
]