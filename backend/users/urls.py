from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuariosListAPIView, UsuarioDetailAPIView, GroupViewSet, UserPermissionsAPIView

router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='groups')

urlpatterns = [
    path('', UsuariosListAPIView.as_view(), name='usuarios-list'),
    path('<int:usuario_id>/', UsuarioDetailAPIView.as_view(), name='usuario-detail'),
    path('<int:usuario_id>/permissions/', UserPermissionsAPIView.as_view(), name='usuario-permissions'),
    path('groups/', GroupViewSet.as_view(), name='group-list'),
    #path('', include(router.urls)),
]