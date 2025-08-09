from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuariosViewSet, GroupAPIView

router = DefaultRouter()
router.register(r'usuarios', UsuariosViewSet, basename='usuarios')

urlpatterns = [
    path('', include(router.urls)),
    path('groups/', GroupAPIView.as_view(), name='group-list'),
]