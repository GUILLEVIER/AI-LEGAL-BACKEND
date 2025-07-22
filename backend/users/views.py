from rest_framework import generics
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from dj_rest_auth.views import LoginView, LogoutView, PasswordChangeView
from core.mixins import StandardResponseMixin
from core.utils import success_response, error_response
from .models import Usuarios
from .serializers import UsuariosSerializer

class UsuariosListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = Usuarios.objects.all() # type: ignore
    serializer_class = UsuariosSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de usuarios",
            unpaginated_message="Listado de usuarios obtenido correctamente",
            code="usuarios_list",
            error_code="usuarios_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Usuario creado exitosamente",
            code="usuario_created",
            error_message="Error al crear el usuario",
            error_code="usuario_create_error",
            http_status=201,
            **kwargs
        )

class UsuarioDetailAPIView(StandardResponseMixin, generics.RetrieveAPIView):
    queryset = Usuarios.objects.all() # type: ignore
    serializer_class = UsuariosSerializer
    lookup_url_kwarg = 'usuario_id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Detalle de usuario obtenido correctamente",
                code="usuario_detail",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el detalle del usuario",
                code="usuario_detail_error",
                http_status=404
            )

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