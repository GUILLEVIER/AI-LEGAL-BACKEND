from rest_framework import generics
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from dj_rest_auth.views import LoginView, LogoutView, PasswordChangeView

from core.utils import success_response, error_response
from .models import Usuarios
from .serializers import UsuariosSerializer

class UsuariosListAPIView(generics.ListCreateAPIView):
    queryset = Usuarios.objects.all() # type: ignore
    serializer_class = UsuariosSerializer

class UsuarioDetailAPIView(generics.RetrieveAPIView):
    queryset = Usuarios.objects.all() # type: ignore
    serializer_class = UsuariosSerializer
    lookup_url_kwarg = 'usuario_id'

class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # Si el login fue exitoso (status 200 o 201)
        if response.status_code in [200, 201]:
            return success_response(
                data=response.data,
                message="Login exitoso",
                code="login_success",
                http_status=response.status_code
            )
        else:
            # Si hubo error, extrae el mensaje de error
            error_msg = response.data.get('non_field_errors') or response.data.get('detail') or "Error de login"
            return error_response(
                errors=error_msg,
                message="Credenciales inválidas",
                code="login_failed",
                http_status=response.status_code
            )

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return success_response(
                data=response.data,
                message="Token refrescado exitosamente",
                code="token_refresh_success",
                http_status=200
            )
        else:
            error_msg = response.data.get('detail') or "Error al refrescar el token"
            return error_response(
                errors=error_msg,
                message="Token inválido o expirado",
                code="token_refresh_failed",
                http_status=response.status_code
            )

class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return success_response(
                data=response.data,
                message="Token verificado exitosamente",
                code="token_verify_success",
                http_status=200
            )
        else:
            error_msg = response.data.get('detail') or "Token inválido"
            return error_response(
                errors=error_msg,
                message="Token inválido",
                code="token_verify_failed",
                http_status=response.status_code
            )

class CustomPasswordChangeView(PasswordChangeView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code in [200, 201]:
            return success_response(
                data=response.data,
                message="Contraseña cambiada exitosamente",
                code="password_change_success",
                http_status=response.status_code
            )
        else:
            error_msg = response.data.get('non_field_errors') or response.data.get('detail') or "Error al cambiar la contraseña"
            return error_response(
                errors=error_msg,
                message="No se pudo cambiar la contraseña",
                code="password_change_failed",
                http_status=response.status_code
            )

class CustomLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code in [200, 201]:
            return success_response(
                data=response.data,
                message="Logout exitoso",
                code="logout_success",
                http_status=response.status_code
            )
        else:
            error_msg = response.data.get('detail') or "Error al cerrar sesión"
            return error_response(
                errors=error_msg,
                message="No se pudo cerrar sesión",
                code="logout_failed",
                http_status=response.status_code
            )