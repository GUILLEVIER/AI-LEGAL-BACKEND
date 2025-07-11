from django.urls import path
from .views import EmpresasListAPIView, PlanesListAPIView

urlpatterns = [
    path('empresas/', EmpresasListAPIView.as_view(), name='empresas-list'),
    path('planes/', PlanesListAPIView.as_view(), name='planes-list'),
]