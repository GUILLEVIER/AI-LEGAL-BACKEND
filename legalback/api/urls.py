from django.urls import path
from . import views

urlpatterns = [
    #path('tribunales/', views.tribunales_list),
    path('tribunales/', views.TribunalesListAPIView.as_view()),
    path('tribunales/info/', views.tribunales_info),
    path('planes/', views.planes_list),
    #path('usuarios/<int:pk>/', views.usuario_detail),
    path('usuarios/<int:usuario_id>/', views.UsuarioDetailAPIView.as_view()),
    path('empresas/', views.empresas_list),
]