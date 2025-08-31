from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuariosViewSet, GroupAPIView, PerfilViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuariosViewSet, basename='usuarios')
router.register(r'perfiles', PerfilViewSet, basename='perfiles')

urlpatterns = [
    path('', include(router.urls)),
    path('groups/', GroupAPIView.as_view(), name='group-list'),
]