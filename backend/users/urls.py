from django.urls import path
from .views import UsuariosListAPIView, UsuarioDetailAPIView

urlpatterns = [
    path('', UsuariosListAPIView.as_view(), name='usuarios-list'),
    path('<int:usuario_id>/', UsuarioDetailAPIView.as_view(), name='usuario-detail'),
]